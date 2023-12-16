from flask_mail import Message
from app import mail, app
from models import User
from flask import render_template, url_for


def send_email(subject='',recipients=[], text_body='', html_body='', sender=''):
  message = Message(subject=subject, recipients=recipients, sender=sender)
  message.body == text_body
  message.html = html_body
  mail.send(message=message)
  
def send_password_reset_email(user:User|None):
  token = user.get_reset_password_token()
  print('reset_token link: ',url_for('reset_password', token=token, _external=True))
  send_email(
    subject='[microblog] reset your password',
    sender= app.config['ADMINS'][0],
    recipients=[user.email],
    text_body= render_template('email/email.txt', user = user, token = token),
    html_body= render_template('email/email.html', user = user, token = token)
  )
