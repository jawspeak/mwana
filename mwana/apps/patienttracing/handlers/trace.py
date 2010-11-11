import re
from rapidsms.contrib.handlers.handlers.keyword import KeywordHandler
from mwana.apps.patienttracing.models import PatientTrace
from datetime import datetime
from rapidsms.models import Contact
from rapidsms.messages.outgoing import OutgoingMessage
from mwana.util import get_clinic_or_default
from mwana.apps.broadcast.models import BroadcastMessage
from mwana.const import get_cba_type

class TraceHandler(KeywordHandler):
    '''
    User sends: 
    TRACE MARY <REASON>
    (Reason is optional)
    Where mary is patient's name.  Message goes out to all CBAs asking them to find and talk to Mary.  
    It also asks them to reply with the message, 
    TOLD MARY
    once they have spoken to the patient and asked them to go to the clinic.
    
    After a set period of time a follow up message will go out of from the system to the CBA that replied
    asking them to follow up with Mary and confirm that she did indeed go to the clinic.
    This is done by having the CBA send the following message to the system:
    CONFIRM MARY
    '''
    
    keyword = "trace|trase|trac"
    PATTERN = re.compile(r"^(\w+)(\s+)(.{1,})(\s+)(\d+)$")  #TODO: FIX ME
    
    help_txt = "Sorry, the system could not understand your message. To trace a patient please send: TRACE <PATIENT_NAME>"
    unrecognized_txt = "Sorry, the system does not recognise your number.  To join the system please send: JOIN"
    response_to_trace_txt = "Thank You %s! Your patient trace has been initiated.  You will be notified when the patient is found."
    cba_initiate_trace_msg = "Hello %s, please find %s and tell them to come to the clinic. When you've told them, please reply to this msg with: TOLD %s"
    
    
    def handle(self,text):
        #check message is valid
        #check for:
        # CONTACT is valid
        # FORMAT is valid
        # 
        #pass it off to trace() for processing.
        self.man_trace(text)
        return True
        
    
    def man_trace(self, name):
        '''
        Initiate a "manual" trace
        '''
    #    create entry in the model (PatientTrace)
    #    send out response message(s)
        p = PatientTrace.objects.create()
        p.initiator = self.msg.connection.contact
        p.type="manual"
        p.name = name
        p.status = "new"
        p.start_date = datetime.now() 
        p.save()
        
        
        self.respond_trace_initiated(name)        
        self.send_trace_to_cbas(name)
     
    def respond_trace_initiated(self,patient_name):
        '''
        Respond with an outgoing message back to the sender that a trace has been initiated
        '''
        
        self.respond(self.response_to_trace_txt % (self.msg.contact.name))
        pass
 
    def send_trace_to_cbas(self, patient_name):
        '''
        Sends CBAs the initiate trace message
        '''
        location = get_clinic_or_default(self.msg.contact)
        
        cbas = Contact.active.location(location).exclude(id=self.msg.contact.id).filter(types=get_cba_type())
        
        
#        cba_initiate_trace_msg = "Hello %s, please find %s and tell them to come
# to the clinic: %s. When you've told them, please reply to this msg with: TOLD %s"

        self.broadcast(self.cba_initiate_trace_msg, cbas, "CBA", patient_name)
 
    def help(self):
        '''
        Respond with a help message in the event of a malformed msg or if no name was supplied
        '''
        self.respond(self.help_txt)
    
    def unrecognized_sender(self):
        '''
        Respond with a message indicating that the sender is not recognized/authorized to initiate
        traces
        '''
        self.respond(self.unrecognized_txt)
        pass
    
    def broadcast(self, text, contacts, group_name, patient_name):
#        message_body = "%(text)s [from %(user)s to %(group)s]"
        message_body = "%(text)s"
        
        for contact in contacts:
            if contact.default_connection is None:
                self.info("Can't send to %s as they have no connections" % contact)
            else:
                OutgoingMessage(contact.default_connection, message_body,
                                **{"text": (text % (contact.name, patient_name, patient_name))}).send()
        
        logger_msg = getattr(self.msg, "logger_msg", None) 
        if not logger_msg:
            self.error("No logger message found for %s. Do you have the message log app running?" %\
                       self.msg)
        bmsg = BroadcastMessage.objects.create(logger_message=logger_msg,
                                               contact=self.msg.contact,
                                               text=text, 
                                               group=group_name)
        bmsg.recipients = contacts
        bmsg.save()
        return True
        

# ====================================================================     
#    DELETE ME!
#
#    initiator = models.ForeignKey(Contact, related_name='patients_traced',
#                                     limit_choices_to={'types__slug': 'clinic_worker'},
#                                     null=True, blank=True)
#    type = models.CharField(max_length=15)
#    name = models.CharField(max_length=50) # name of patient to trace
#    patient_event = models.ForeignKey(PatientEvent, related_name='patient_traces',
#                                      null=True, blank=True) 
#    messenger = models.ForeignKey(Contact,  related_name='patients_reminded',
#                            limit_choices_to={'types__slug': 'cba'}, null=True,
#                            blank=True)# cba who informs patient
#
#    confirmed_by = models.ForeignKey(Contact, related_name='patient_traces_confirmed',
#                            limit_choices_to={'types__slug': 'cba'}, null=True,
#                            blank=True)# cba who confirms that patient visited clinic
#
#    status = models.CharField(choices=STATUS_CHOICES, max_length=15) # status of tracing activity
#
#    start_date = models.DateTimeField() # date when tracing starts
#    reminded_on = models.DateTimeField(null=True, blank=True) # date when cba tells mother
#    confirmed_date = models.DateTimeField(null=True, blank=True)# date of confirmation that patient visited clinic   
#    
# =======================================================================    
    
    