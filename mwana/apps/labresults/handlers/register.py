#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from rapidsms.contrib.handlers import KeywordHandler
from rapidsms.contrib.locations.models import Location
from rapidsms.models import Contact
import re


class RegisterHandler(KeywordHandler):
    """
    """

    keyword = "join"

    PATTERN = re.compile(r"^(\w+)(\s+)(.{4,})(\s+)(\d+)$")
    HELP_TEXT = "To register, send JOIN <CLINIC CODE> <NAME> <SECURITY CODE>"
    PIN_LENGTH = 4
    
    def help(self):
        self.respond(self.HELP_TEXT)

    def mulformed_msg_help(self):
        self.respond("Sorry, I didn't understand that. "
            "Make sure you send your location, name and pin "
            "like: JOIN <CLINIC CODE> <NAME> <SECURITY CODE>.")

    def handle(self, text):
        if self.msg.contact is not None:
            self.respond("I already have a contact with phone %(identity)s.", identity=self.msg.connection.identity)
            return
        text=text.strip()
        group=self.PATTERN.search(text)
        if group is None:
            self.mulformed_msg_help()
            return

        tokens=group.groups()
        if not tokens:
            self.mulformed_msg_help()
            return

        clinic_code=tokens[0].strip()
        name=tokens[2]
        name=name.title().strip()
        pin=tokens[4].strip()
        if len(pin)!= self.PIN_LENGTH:
            self.respond("Sorry, %(pin)s wasn't a valid security code. "
            "Please make sure your code is a %(count)s-digit number like %(sample)s. "
            "Send JOIN <CLINIC CODE> <YOUR NAME> <SECURITY CODE>.",pin=pin,
            count=self.PIN_LENGTH, sample=''.join(str(i) for i in range(1,int(self.PIN_LENGTH)+1)))
            return
        try:
            location = Location.objects.get(slug__iexact=clinic_code)
            contact = Contact.objects.create(name=name, location=location, pin=pin)
            self.msg.connection.contact = contact
            self.msg.connection.save()
            self.respond("Hi %(name)s, thanks for registering for DBS "
            "results from Results160 as staff of %(location)s. "
            "Reply with keyword 'HELP' if your information is not "
            "correct.", name=contact.name, location=location.name)
        except Location.DoesNotExist:
            self.respond("Sorry, I don't know about a location with code %(code)s. Please check your code and try again.",
                         code=clinic_code)

        