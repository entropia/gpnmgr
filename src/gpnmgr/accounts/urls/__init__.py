from typing import Any, List

from django.urls import path

from gpnmgr.accounts.views.account_request import AccountRequestView, AccountRequestListView, RevokeAccountRequestView, \
    AccountRequestConfirmView
from gpnmgr.accounts.views.auth import AuthorizeSSOUser, UserLoginView, UserLogoutView
from gpnmgr.accounts.views.autocomplete_search import UserSearchView
from gpnmgr.accounts.views.profile import UserProfileView


urlpatterns: List[Any] = [
    # auth
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    # profile
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    # sso
    path('auth/', AuthorizeSSOUser.as_view(), name='auth'),
    path('search/<str:query>/', UserSearchView.as_view(), name='search'),
    path('invite', AccountRequestView.as_view(), name='user_invite'),
    path('confirm/<uuid:pk>/<uuid:verification>', AccountRequestConfirmView.as_view(), name='user_invite_confirm'),
    path('invitations/', AccountRequestListView.as_view(), name='user_invitations'),
    path('invitations/revoke/<uuid:pk>', RevokeAccountRequestView.as_view(), name='user_invite_revoke'),
]
