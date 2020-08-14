from threading import Thread
from flask import current_app, render_template
from flask_mail import Message

from demo.app import mail
from demo.extensions import celery

@celery.task()
def send_async_email(kwargs):
    msg = Message(kwargs['subject'], sender=kwargs['sender'], recipients=kwargs['recipients'])
    msg.html = render_template(kwargs['template'] + '.txt', **kwargs)
    msg.body = render_template(kwargs['template'] + '.html', **kwargs)
    mail.send(msg)


def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    msg_kwargs = {
        'subject': app.config['MAIL_SUBJECT_PREFIX'] + ' ' + subject,
        'sender': app.config['MAIL_SENDER_DEFAULT'],
        'recipients': [to],
        'template': template
    }
    msg_kwargs.update(kwargs)
    send_async_email.delay(msg_kwargs)
