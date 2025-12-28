from auditlog.models import LogEntry

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import ListView
from django.utils.translation import gettext_lazy as _

class LogView(PermissionRequiredMixin, ListView):
    model = LogEntry
    object: LogEntry
    extra_context = {
        'title': _('Auditlog'),
    }
    template_name = 'log/log_list.html'
    permission_required = 'log.view_log'
