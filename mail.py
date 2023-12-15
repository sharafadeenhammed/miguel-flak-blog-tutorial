from flask_mail import Message
from app import mail


def send_email(subject='',recipients=[], text_body='', html_body='', sender=''):
  message = Message(subject=subject, recipients=recipients, sender=sender)
  message.body == text_body
  message.html = html_body
  mail.send(message=message)