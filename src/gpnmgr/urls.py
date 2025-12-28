"""
URL configuration for gpnmgr project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from typing import List, Any

from django.conf import settings
from django.urls import path, include

from gpnmgr.accounts.views.landing_page import LandingPageView

urlpatterns: List[Any] = [
    path('', LandingPageView.as_view(), name='landing_page'),
    path('teams/', include('gpnmgr.teams.urls')),
    path('log/', include('gpnmgr.log.urls')),
    path('user/', include('gpnmgr.accounts.urls')),
    path('i18n/', include('django.conf.urls.i18n')),
]
