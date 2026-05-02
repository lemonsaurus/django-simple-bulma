"""URL configuration for the Playwright end-to-end test page."""

from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    path("", TemplateView.as_view(template_name="e2e_page.html"), name="e2e"),
]
