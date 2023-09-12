from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string



def get_subscribers(category):
    user_emails = []
    for user in category.subscribers.all():
        user_emails.append(user.email)

    return user_emails

def new_post_subscription(instance):
    template = 'mail/newpost.html'

    for category in instance.postCategory.all():
        email_subject = f'Новый пост в категории {category}'
        user_emails = get_subscribers(category)

        html = render_to_string(
            template_name=template,
            context={
                'category': category,
                'post': instance,
            }
        )
        msg = EmailMultiAlternatives(
            subject=email_subject,
            body='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=user_emails,
        )

        msg.attach_alternative(html, 'text/html')
        msg.send()

# def send_week_mails():
#     print('Hello from background task!')