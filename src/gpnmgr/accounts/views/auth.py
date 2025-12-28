from __future__ import annotations

import re
from json import JSONDecodeError
from typing import Any, Optional

from authlib.integrations.base_client import OAuthError
from authlib.integrations.django_client import OAuth
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login as login_user, REDIRECT_FIELD_NAME, logout
from django.contrib.auth.models import AbstractUser, Group
from django.contrib.auth.views import LoginView, UserModel
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import RedirectView

from gpnmgr.accounts.models import User


class UserLoginView(LoginView):
    redirect_authenticated_user = True
    title = _('Login')

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        redirect_to = self.get_redirect_url()
        redirect_uri = request.build_absolute_uri(reverse('auth'))
        redirect_uri += f'?{REDIRECT_FIELD_NAME}={redirect_to}'
        oauth_client = getattr(oauth, settings.OAUTH_NAME)
        return oauth_client.authorize_redirect(request, redirect_uri)


oauth = OAuth()
oauth.register(
    name=settings.OAUTH_NAME,
    client_id=settings.OAUTH_NAME,
    client_secret=settings.OAUTH_SECRET,
    server_metadata_url=settings.OPENID_CONF_URL,
    client_kwargs={
        'scope': settings.OAUTH_CLIENT_SCOPES,
    }
)


class AuthorizeSSOUser(RedirectView):

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        try:
            user = self.authenticate(request)
            if user is None:
                messages.error(request, _('Error while creating the user instance!'))
                return HttpResponseRedirect(settings.LOGIN_URL)
            redirect_to = request.GET.get(REDIRECT_FIELD_NAME)
            login_user(self.request, user) # type: ignore[arg-type]
            messages.success(request, _('Successfully logged in!'))
            return HttpResponseRedirect(redirect_to or settings.LOGIN_REDIRECT_URL)
        except OAuthError as e:
            messages.error(request, _('Error while trying to authenticate with sso! %(message)s') % {
                'message': str(e)
            })
            return HttpResponseRedirect(settings.LOGIN_URL)

    def authenticate(self, request: HttpRequest) -> Optional[AbstractUser]:
        try:
            oauth_client = getattr(oauth, settings.OAUTH_NAME)
            token = oauth_client.authorize_access_token(request)
            if 'userinfo' in token:
                return self._populate_user(token['userinfo'])
        except JSONDecodeError:
            pass
        return None

    @staticmethod
    def _populate_user(user_data: dict[str, Any]) -> AbstractUser:
        username = user_data.get(settings.OAUTH_USERNAME_CLAIM, '')
        groups: list[str] = user_data.get(settings.OAUTH_GROUP_CLAIM, [])
        for group in groups:
            if re.match(settings.OAUTH_GROUP_IGNORE_REGEX, group) is None:
                Group.objects.get_or_create(name=group)
        try:
            user: AbstractUser = User.objects.get_by_natural_key(username)
        except UserModel.DoesNotExist: # type: ignore[attr-defined]
            user = User.objects.create(username=username)
            user.set_unusable_password()
            user.display_name = user_data.get(settings.OAUTH_DISPLAY_NAME_CLAIM, '')
        user.email = user_data.get(settings.OAUTH_EMAIL_CLAIM, '')
        user.groups.set(Group.objects.filter(name__in=groups))
        user.is_superuser = False
        user.is_staff = False
        user.save()
        return user

class UserLogoutView(RedirectView):
    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        logout(request)
        return redirect(reverse('landing_page'))
