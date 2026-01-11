from typing import Any, List

from django.urls import path

from gpnmgr.mastodon.views.mastodon import MastodonListView, MastodonCreateView, MastodonDetailView, MastodonModifyView, \
    MastodonUserAddView, MastodonUserRemoveView

urlpatterns: List[Any] = [
    # mastodon
    path('list', MastodonListView.as_view(), name="mastodon_list"),
    path('create', MastodonCreateView.as_view(), name="mastodon_create"),
    path('detail/<uuid:pk>', MastodonDetailView.as_view(), name="mastodon_detail"),
    path('edit/<uuid:pk>', MastodonModifyView.as_view(), name="mastodon_edit"),
    path('user_add/<uuid:pk>', MastodonUserAddView.as_view(), name="mastodon_user_add"),
    path('user_remove/<uuid:pk>/<str:user>', MastodonUserRemoveView.as_view(), name="mastodon_user_remove"),
]