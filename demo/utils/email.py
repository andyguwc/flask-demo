from threading import Thread
from flask import current_app, render_template
from flask_mail import Message

from demo.app import mail


# using threading to send emails
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    msg = Message(
        app.config['MAIL_SUBJECT_PREFIX'] + ' ' + subject,
        sender=app.config['MAIL_SENDER_DEFAULT'], 
        recipients=[to]
    )   
    msg.html = render_template(template + '.txt', **kwargs)
    msg.body = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr
