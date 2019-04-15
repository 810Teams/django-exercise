"""
    `urls.py`
    Contains URLs in `polls` application
"""

from django.urls import path

from . import views

urlpatterns = [
    path('index/', views.index, name='index'),
    path('detail/<int:poll_id>/', views.detail, name='detail')
]
