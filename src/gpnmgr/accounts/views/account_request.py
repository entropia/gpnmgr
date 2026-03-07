from typing import Any

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import JsonResponse, HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import CreateView, ListView, FormView

from gpnmgr.accounts.forms.account_request_confirm import AccountRequestConfirmForm
from gpnmgr.accounts.models import User
from gpnmgr.accounts.models.request import AccountRequest
from gpnmgr.settings import LDAP_CONNECTION


class AccountRequestView(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    model = AccountRequest
    object: AccountRequest
    template_name = 'request/account_invite.html'
    http_method_names = ('get', 'post', )

    fields = ['name', 'email', 'invite_text', 'team']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['invite_form'] = self.get_form(self.get_form_class())
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['name'].required = False
        form.fields['team'].required = True
        if not self.request.user.has_perm('teams.manage_teams'):
            form.fields['team'].queryset = self.request.user.team_admins.all()
        return form

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string(self.template_name, {'invite_form': form, 'object': self.object}, request=self.request)
            return JsonResponse({'success': False, 'html': html})
        return super().form_invalid(form)

    def form_valid(self, form):
        form.instance.inviter = self.request.user
        self.object = form.save()
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            messages.success(self.request, _('Successfully invited %(user)s') % {
                'user': self.object.name
            })
            return JsonResponse({'success': True})
        return super().form_valid(form)

    def has_permission(self):
        if self.request.user.team_admins.count() > 0:
            return True
        if self.request.user.has_perm('teams.manage_teams'):
            return True
        return self.request.user.has_perm('accounts.manage_requests')

class AccountRequestListView(PermissionRequiredMixin, LoginRequiredMixin, ListView):
    model = AccountRequest
    object: AccountRequest

    template_name = 'request/invite_list.html'
    http_method_names = ('get', )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['title'] = _('User invitations')
        return context

    def has_permission(self):
        if self.request.user.sent_invites.count() > 0:
            return True
        return self.request.user.has_perm('accounts.manage_requests')

    def get_queryset(self):
        if self.request.user.has_perm('accounts.manage_requests'):
            return AccountRequest.objects.all()
        return self.request.user.sent_invites.all()

class RevokeAccountRequestView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'accounts.manage_requests'
    http_method_names = ('get', )

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        account_request = get_object_or_404(AccountRequest, pk=kwargs['pk'])
        account_request.is_revoked = True
        account_request.save()

        messages.success(request, _('Successfully revoked invite for %(user)s') % {
            'user': account_request.name
        })

        return HttpResponseRedirect(reverse_lazy('user_invitations'))

    def has_permission(self):
        if self.request.user == get_object_or_404(AccountRequest, pk=self.kwargs.get('pk')).inviter:
            return True
        return self.request.user.has_perm('accounts.manage_requests')

class AccountRequestConfirmView(FormView):
    form_class = AccountRequestConfirmForm
    template_name = 'request/account_confirm.html'

    def __init__(self):
        super().__init__()
        self.a_r = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['confirm_form'] = self.get_form(self.get_form_class())
        return context

    def get_form(self, form_class = None):
        form = super().get_form(form_class)
        form.fields['email'].initial = self.a_r.email
        form.fields['username'].initial = self.a_r.name
        return form

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        self.a_r = get_object_or_404(AccountRequest, pk=kwargs['pk'])
        if (not self.a_r.is_valid) or self.a_r.verification_code != kwargs['verification']:
            return HttpResponseRedirect(reverse_lazy('landing_page'), status=403)
        return super().get(request, *args, **kwargs)

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        self.a_r = get_object_or_404(AccountRequest, pk=kwargs['pk'])
        if (not self.a_r.is_valid) or self.a_r.verification_code != kwargs['verification']:
            return HttpResponseRedirect(reverse_lazy('landing_page'), status=403)
        return super().post(request, *args, **kwargs)

    def form_valid(self, form: AccountRequestConfirmForm):
        conn = LDAP_CONNECTION
        conn.bind()

        user_dn = f'{settings.LDAP_USER_PK}={form.cleaned_data.get('username')},{settings.LDAP_USER_OU},{settings.LDAP_BASE_DN}'
        object_classes = ['top', settings.LDAP_USER_OBJECT_CLASS, settings.LDAP_MASTODON_OBJECT_CLASS] + settings.LDAP_USER_ADDITIONAL_OBJECT_CLASSES

        conn.add(
            user_dn,
            object_classes,
            {
                settings.LDAP_USER_PK: form.cleaned_data.get('username'),
                settings.LDAP_USER_MAIL_PK: self.a_r.email,
                settings.LDAP_USER_NAME_PK: form.cleaned_data.get('display_name'),
                settings.LDAP_USER_DISPLAY_NAME_PK: form.cleaned_data.get('display_name'),
                settings.LDAP_USER_PASSWORD_PK: get_random_string(64),
            }
        )

        conn.extend.standard.modify_password(user_dn, new_password=form.cleaned_data.get('password'))

        if int(conn.result.get('result')) != 0:
            messages.error(self.request, _('Error creating the user object in LDAP. Please try again later. Contact us if the error persists. Error code %(result)s: %(message)s') % {
                'result': conn.result.get('result'),
                'message': conn.result.get('description'),
            })
            return HttpResponseRedirect(reverse_lazy('landing_page'))

        new_user = User.objects.create(
            username=form.cleaned_data.get('username'),
            last_name=form.cleaned_data.get('display_name'),
            display_name=form.cleaned_data.get('display_name'),
            email=self.a_r.email,
            object_dn=user_dn
        )
        new_user.set_unusable_password()
        new_user.save()

        self.a_r.team.members.add(new_user)
        self.a_r.team.save()

        self.a_r.confirmed_at = timezone.now()
        self.a_r.save()

        messages.success(self.request, _('Your account has been created successfully. It might take a few minutes until it is fully synchronized and active.'))

        return HttpResponseRedirect(reverse_lazy('landing_page'))