# vim: ai ts=4 sts=4 et sw=4
import re

from django.conf import settings

from rapidsms.contrib.handlers.handlers.keyword import KeywordHandler

from mwana.apps.labresults.models import SampleNotification
from mwana.apps.stringcleaning.inputcleaner import InputCleaner
from mwana.util import get_clinic_or_default

UNGREGISTERED = "Sorry, you must be registered with Results160 to report DBS samples sent. If you think this message is a mistake, respond with keyword 'HELP'"
SENT          = "Hello %(name)s! We received your notification that %(count)s DBS samples were sent to us today from %(clinic)s. We will notify you when the results are ready."
HELP          = "To report DBS samples sent, send SENT <NUMBER OF SAMPLES>"
SORRY         = "Sorry, we didn't understand that message."

class SentHandler(KeywordHandler):
    """
    """

    keyword = "sent|send|sen|snt|cent|snd"

    def help(self):
        self.respond(HELP)

    def get_only_number(self, text):
       reg = re.compile(r'\d+')
       nums = reg.findall(text)
       if len(nums) == 1:
           return nums[0]
       else:
           return None

    def handle(self, text):
        original_text = text
        if not self.msg.contact:
            self.respond(UNGREGISTERED)
            return
        b = InputCleaner()
        try:
            text = b.remove_dash_plus(text)
            count = int(b.try_replace_oil_with_011(text))
        except ValueError:
            text = b.words_to_digits(text)
            if not text:
                text= self.get_only_number(original_text)
                if text:
                    count = int(text)
                else:
                    self.respond("%s %s" % (SORRY, HELP))
                    return
            else:
                self.info("Converted %s to %s" % (original_text, text))
                count = int(text)
                count = abs(count) #just in case we change our general cleaning routine           
        
        if count < 1:
            self.respond("Sorry, the number of DBS samples sent must be greater than 0 (zero).")
            return
        
        max_len = settings.MAX_SMS_LENGTH
        # record this in our records    
        SampleNotification.objects.create(contact=self.msg.contact, 
                                          location=self.msg.contact.location,
                                          count=count, count_in_text=
                                          original_text[0:max_len])
        clinic = get_clinic_or_default(self.msg.contact)
        self.respond(SENT, name=self.msg.contact.name, count=count,
                     clinic=clinic)
                     
        