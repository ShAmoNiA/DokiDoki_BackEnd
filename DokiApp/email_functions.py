from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template

from DokiDoki.settings import DOKI_APP_BASE_URL
from DokiDoki.settings import EMAIL_HOST_USER
from DokiDoki.settings import HOST, PORT


def send_email(subject, message, to_list, html_content):
    message = EmailMultiAlternatives(subject,
                                     message,
                                     EMAIL_HOST_USER,
                                     to_list)
    message.attach_alternative(html_content, "text/html")
    message.send()


def send_text_email(subject, message, to_list):
    for address in to_list:
        message = EmailMultiAlternatives(subject,
                                         message,
                                         EMAIL_HOST_USER,
                                         [address])
        message.send()


def send_verification_email(user):
    message = "Hello " + user.fullname + ". please click on the button below to verify your email"
    context = {'HOST': HOST,
               'PORT': PORT,
               'email': user.email,
               'name': user.username,
               'action': 'verify_email',
               'app_base_url': DOKI_APP_BASE_URL,
               'token': user.verify_email_token}
    html_content = get_template('email_template.html').render(context=context)

    send_email("Verify email", message, [user.email], html_content)
