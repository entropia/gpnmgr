from django.views.generic import TemplateView
from django.utils.translation import gettext_lazy as _

class LandingPageView(TemplateView):
    template_name = 'landing_page.html'
    title = _('Start')
