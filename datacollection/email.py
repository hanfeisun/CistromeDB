"""
SYNOPSIS: this module is a simple emailer for newdc
"""

from django.core.mail import send_mail

def newdc_email(subject, msg, recipients_list):
    send_mail(subject, msg, "cistrome_dc@jimmy.harvard.edu",
              recipients_list)
