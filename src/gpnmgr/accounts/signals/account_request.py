from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from gpnmgr.accounts.models.request import AccountRequest


# Send invite email on creation
@receiver(post_save, sender=AccountRequest)
async def email_invite_on_creation(sender, instance, created, **kwargs):
    if created:
        invite_link = settings.USER_INVITE_BASE_URL + reverse_lazy('user_invite_confirm',
                                                                   kwargs={
                                                                       'pk': instance.pk,
                                                                       'verification': instance.verification_code,
                                                                   })
        context = {
            "name": instance.name,
            "inviter_name": instance.inviter,
            "invite_message": instance.invite_text,
            "invite_link": invite_link,
            "team": instance.team
        }
        text_content = render_to_string(
            "request/account_invite_email.txt",
            context=context
        )
        html_content = render_to_string(
            "request/account_invite_email.html",
            context=context
        )
        msg = EmailMultiAlternatives(
            subject=_('accounts.request.invite_subject'),
            body=text_content,
            from_email=settings.USER_INVITE_FROM_EMAIL,
            to=[instance.email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()