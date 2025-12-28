from typing import Any, List

from django.urls import path

from gpnmgr.teams.views.teams import TeamListView, TeamDetailView, TeamModifyView, TeamCreateView, TeamMemberAddView, \
    TeamMemberRemoveView, TeamMemberPromoteView, TeamMemberDemoteView

urlpatterns: List[Any] = [
    # teams
    path('list', TeamListView.as_view(), name="teams_list"),
    path('create', TeamCreateView.as_view(), name="teams_create"),
    path('detail/<uuid:pk>', TeamDetailView.as_view(), name="team_detail"),
    path('edit/<uuid:pk>', TeamModifyView.as_view(), name="team_edit"),
    path('member_add/<uuid:pk>', TeamMemberAddView.as_view(), name="team_member_add"),
    path('member_remove/<uuid:pk>/<str:member>', TeamMemberRemoveView.as_view(), name="team_member_remove"),
    path('member_promote/<uuid:pk>/<str:member>', TeamMemberPromoteView.as_view(), name="team_member_promote"),
    path('member_demote/<uuid:pk>/<str:member>', TeamMemberDemoteView.as_view(), name="team_member_demote"),
]