from typing import Any, Dict

from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.http import JsonResponse, HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import CreateView, ListView, DetailView, UpdateView

from gpnmgr.accounts.models import User
from gpnmgr.teams.forms.add_member_form import TeamMemberAddForm
from gpnmgr.teams.models import Team


class TeamCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Team
    object: Team
    # TODO: Add permission denied message to AJAX response
    permission_required = 'teams.manage_teams'
    success_url = reverse_lazy('teams_list')
    template_name = 'teams/team_create.html'
    http_method_names = ('get', 'post', )

    fields = ['name', 'slug', 'cost_center', 'primary_contact', 'ldap_name']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_form'] = self.get_form(self.get_form_class())
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['slug'].required = False
        form.fields['cost_center'].required = False
        form.fields['primary_contact'].required = False
        form.fields['ldap_name'].required = False
        return form

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string(self.template_name, {'create_form': form}, request=self.request)
            return JsonResponse({'success': False, 'html': html})
        return super().form_invalid(form)

    def form_valid(self, form):
        self.object = form.save()
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        return super().form_valid(form)

class TeamModifyView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Team
    object: Team
    # TODO: Add permission denied message to AJAX response
    permission_required = 'teams.manage_teams'
    success_url = reverse_lazy('teams_list')
    template_name = 'teams/team_modify.html'
    http_method_names = ('get', 'post', )

    fields = ['name', 'slug', 'cost_center', 'primary_contact', 'ldap_name']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['modify_form'] = self.get_form(self.get_form_class())
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['slug'].required = False
        form.fields['cost_center'].required = False
        form.fields['primary_contact'].required = False
        if self.object.ldap_name is not None:
            form.fields['ldap_name'].disabled = True
        else:
            form.fields['ldap_name'].required = False
        return form

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string(self.template_name, {'modify_form': form, 'object': self.object}, request=self.request)
            return JsonResponse({'success': False, 'html': html})
        return super().form_invalid(form)

    def form_valid(self, form):
        self.object = form.save()
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        return super().form_valid(form)

class TeamListView(LoginRequiredMixin, ListView):
    model = Team
    object: Team

    template_name = 'teams/team_list.html'
    http_method_names = ('get', )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['title'] = _('Teams')

        create_view = TeamCreateView()
        create_view.request = self.request
        form = create_view.get_form(create_view.get_form_class())

        context['create_form'] = form
        return context

class TeamDetailView(LoginRequiredMixin, DetailView):
    model = Team
    object: Team
    template_name = 'teams/team_detail.html'
    http_method_names = ('get', )

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = f"{_('Team')} {self.object}"

        modify_form = TeamModifyView(object=self.object)
        modify_form.request = self.request
        modify_form = modify_form.get_form(modify_form.get_form_class())

        member_add_form = TeamMemberAddView(object=self.object)
        member_add_form.request = self.request
        member_add_form = member_add_form.get_form(member_add_form.get_form_class())

        context['modify_form'] = modify_form
        context['member_add_form'] = member_add_form

        context['is_team_admin'] = self.request.user in get_object_or_404(Team, pk=self.kwargs.get('pk')).admins.all() or self.request.user.has_perm('teams.manage_teams')

        return context

class TeamMemberAddView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Team
    object: Team
    template_name = 'teams/team_member_add.html'
    form_class = TeamMemberAddForm
    http_method_names = ('get', 'post', )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['member_add_form'] = self.get_form(self.get_form_class())
        return context

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string(self.template_name, {'member_add_form': form, 'object': self.object}, request=self.request)
            return JsonResponse({'success': False, 'html': html})
        return super().form_invalid(form)

    def form_valid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            current_members = self.object.members.all()
            new_members = form.cleaned_data.get('members',[])
            diff_members = [str(member) for member in new_members if member not in current_members]
            if len(diff_members) > 0:
                self.object = form.save()
                messages.success(self.request, _('Successfully added %(member)s to team')  % {
                    'member': ', '.join(diff_members)
                })
            return JsonResponse({'success': True})
        return super().form_valid(form)

    # TODO: Add permission denied message to AJAX response
    def has_permission(self):
        if self.request.user in get_object_or_404(Team, pk=self.kwargs.get('pk')).admins.all():
            return True
        return self.request.user.has_perm('teams.manage_teams')

    def get_success_url(self):
        return reverse_lazy('team_detail', kwargs={'pk': self.object.id})

class TeamMemberRemoveView(LoginRequiredMixin, PermissionRequiredMixin, View):
    http_method_names = ('get', )

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        team = get_object_or_404(Team, pk=kwargs['pk'])
        member = get_object_or_404(User, pk=kwargs['member'])
        if member in team.members.all():
            if member in team.admins.all():
                if self.request.user.has_perm('teams.manage_teams'):
                    team.admins.remove(member)
                else:
                    messages.error(request, _('You don\'t have permissions to remove admin %(user)s from team') % {})
                    return HttpResponseRedirect(reverse_lazy('team_detail', kwargs={'pk': team.id}))
            team.members.remove(member)
            team.save()
            messages.success(request, _('Successfully removed %(user)s') % {
                'user': member
            })
        else:
            messages.error(request, _('%(user)s was not a member of the team') % {
                'user': member
            })

        return HttpResponseRedirect(reverse_lazy('team_detail', kwargs={'pk': kwargs['pk']}))

    def has_permission(self):
        if self.request.user in get_object_or_404(Team, pk=self.kwargs.get('pk')).admins.all():
            return True
        return self.request.user.has_perm('teams.manage_teams')

class TeamMemberPromoteView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'teams.manage_teams'
    http_method_names = ('get', )

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        team = get_object_or_404(Team, pk=kwargs['pk'])
        member = get_object_or_404(User, pk=kwargs['member'])
        if member in team.admins.all():
            messages.info(request, _('%(user)s is already admin of the team') % {
                'user': member
            })
            return HttpResponseRedirect(reverse_lazy('team_detail', kwargs={'pk': kwargs['pk']}))

        if member in team.members.all():
            team.admins.add(member)
            team.save()

            messages.success(request, _('Successfully promoted %(user)s') % {
                'user': member
            })

        else:
            messages.error(request, _('%(user)s is not a member of the team') % {
                'user': member
            })

        return HttpResponseRedirect(reverse_lazy('team_detail', kwargs={'pk': kwargs['pk']}))

class TeamMemberDemoteView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'teams.manage_teams'
    http_method_names = ('get', )

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        team = get_object_or_404(Team, pk=kwargs['pk'])
        member = get_object_or_404(User, pk=kwargs['member'])
        if member in team.admins.all():
            team.admins.remove(member)
            team.save()
            messages.success(request, _('Successfully demoted %(user)s') % {
                'user': member
            })

        return HttpResponseRedirect(reverse_lazy('team_detail', kwargs={'pk': kwargs['pk']}))
