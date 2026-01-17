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
from gpnmgr.mastodon.forms.add_user_form import MastodonUserAddForm
from gpnmgr.mastodon.models import Mastodon


class MastodonCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Mastodon
    object: Mastodon
    # TODO: Add permission denied message to AJAX response
    permission_required = 'mastodon.manage_accounts'
    success_url = reverse_lazy('mastodon_list')
    template_name = 'mastodon/account_create.html'
    http_method_names = ('get', 'post', )

    fields = ['name', 'description', ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_form'] = self.get_form(self.get_form_class())
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['description'].required = False
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

class MastodonModifyView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Mastodon
    object: Mastodon
    # TODO: Add permission denied message to AJAX response
    permission_required = 'mastodon.manage_accounts'
    success_url = reverse_lazy('mastodon_list')
    template_name = 'mastodon/account_modify.html'
    http_method_names = ('get', 'post', )

    fields = ['name', 'description', ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['modify_form'] = self.get_form(self.get_form_class())
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['name'].disabled = True
        form.fields['description'].required = False

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

class MastodonListView(LoginRequiredMixin, ListView):
    model = Mastodon
    object: Mastodon

    template_name = 'mastodon/account_list.html'
    http_method_names = ('get', )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['title'] = _('Mastodon accounts')

        create_view = MastodonCreateView()
        create_view.request = self.request
        form = create_view.get_form(create_view.get_form_class())

        context['create_form'] = form
        return context

class MastodonDetailView(LoginRequiredMixin, DetailView):
    model = Mastodon
    object: Mastodon
    template_name = 'mastodon/account_detail.html'
    http_method_names = ('get', )

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = f"{_('Mastodon account')} {self.object}"

        modify_form = MastodonModifyView(object=self.object)
        modify_form.request = self.request
        modify_form = modify_form.get_form(modify_form.get_form_class())

        user_add_form = MastodonUserAddView(object=self.object)
        user_add_form.request = self.request
        user_add_form = user_add_form.get_form(user_add_form.get_form_class())

        context['modify_form'] = modify_form
        context['user_add_form'] = user_add_form

        context['is_account_user'] = self.request.user in set(self.object.users.all()) or self.request.user.has_perm('mastodon.manage_accounts')

        return context

class MastodonUserAddView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Mastodon
    object: Mastodon
    template_name = 'mastodon/account_user_add.html'
    form_class = MastodonUserAddForm
    http_method_names = ('get', 'post', )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_add_form'] = self.get_form(self.get_form_class())
        return context

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string(self.template_name, {'user_add_form': form, 'object': self.object}, request=self.request)
            return JsonResponse({'success': False, 'html': html})
        return super().form_invalid(form)

    def form_valid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            current_users = self.object.users.all()
            new_users = form.cleaned_data.get('users',[])
            diff_users = [str(user) for user in new_users if user not in current_users]
            if len(diff_users) > 0:
                self.object = form.save()
                messages.success(self.request, _('Successfully added %(user)s to account')  % {
                    'user': ', '.join(diff_users)
                })
            return JsonResponse({'success': True})
        return super().form_valid(form)

    # TODO: Add permission denied message to AJAX response
    def has_permission(self):
        if self.request.user in get_object_or_404(Mastodon, pk=self.kwargs.get('pk')).users.all():
            return True
        return self.request.user.has_perm('mastodon.manage_accounts')

    def get_success_url(self):
        return reverse_lazy('mastodon_detail', kwargs={'pk': self.object.id})

class MastodonUserRemoveView(LoginRequiredMixin, PermissionRequiredMixin, View):
    http_method_names = ('get', )

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        mastodon = get_object_or_404(Mastodon, pk=kwargs['pk'])
        user = get_object_or_404(User, pk=kwargs['user'])

        if user in mastodon.users.all():
            mastodon.users.remove(user)
            mastodon.save()
            messages.success(request, _('Successfully removed %(user)s') % {
                'user': user
            })
        else:
            messages.error(request, _('%(user)s was not a user of the account') % {
                'user': user
            })

        return HttpResponseRedirect(reverse_lazy('mastodon_detail', kwargs={'pk': kwargs['pk']}))

    def has_permission(self):
        if self.request.user in get_object_or_404(Mastodon, pk=self.kwargs.get('pk')).users.all():
            return True
        return self.request.user.has_perm('mastodon.manage_accounts')

