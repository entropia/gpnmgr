from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic import View

from ..models.user import User

class UserSearchView(LoginRequiredMixin, PermissionRequiredMixin, View):
    model = User
    object: User
    permission_required = 'teams.manage_teams'

    template_name = 'teams/team_list.html'
    http_method_names = ('get', )

    MIN_QUERY_LENGTH = 3
    MAX_RESULTS = 10


    def get(self, request, query, *args, **kwargs):
        query = query.strip()

        if len(query) < self.MIN_QUERY_LENGTH:
            return JsonResponse({'results': [], 'error': 'Query is too short'})

        queryset = User.objects.filter(Q(username__icontains=query) | Q(display_name__icontains=query))[:self.MAX_RESULTS]

        results = [{'username': user.username, 'display_name': user.display} for user in queryset.all()]

        return JsonResponse({'results': results})

