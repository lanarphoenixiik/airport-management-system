"""
URL configuration for airport_system project.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('board/', TemplateView.as_view(template_name='board.html'), name='board'),
]