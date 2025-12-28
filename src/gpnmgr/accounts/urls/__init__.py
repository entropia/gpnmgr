from typing import Any, List

from django.urls import path

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
]
