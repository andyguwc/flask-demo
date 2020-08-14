from flask import current_app, render_template
from flask_mail import Message

from demo.app import mail
from demo.extensions import celery

@celery.task
def send_async_email(email_data):
    msg = Message(email_data['subject'], sender=email_data['sender'], recipients=email_data['recipients'])
    msg.body = email_data['body']
    msg.html = email_data['html']
    mail.send(msg)


def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    email_data = {
        'subject': app.config['MAIL_SUBJECT_PREFIX'] + ' ' + subject,
        'sender': app.config['MAIL_SENDER_DEFAULT'],
        'recipients': [to],
        'body': render_template(template + '.txt', **kwargs),
        'html': render_template(template + '.html', **kwargs)
    }
    send_async_email.delay(email_data)

