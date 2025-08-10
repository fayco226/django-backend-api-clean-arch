"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from exemple.views import ExempleView  # Added this line per instructions

urlpatterns = [
    
    path('exemple/<str:ressource>/', ExempleView.as_view({'get': 'index'}), name='adm_index'),  # Corrected spelling
    path('exemple/<str:ressource>/<int:id>/', ExempleView.as_view({'get': 'display'}), name='adm_display'),
    path('api/exemple/many/<str:ressource>/', ExempleView.as_view({'get': 'get_many'}), name='adm_get_many'),
    path('api/exemple/one/<str:ressource>/', ExempleView.as_view({'get': 'get_one'}), name='adm_get_one'),
    path('api/exemple/<str:ressource>/', ExempleView.as_view({'post': 'store'}), name='adm_store'),
    path('api/exemple/<str:ressource>/<int:id>/', ExempleView.as_view({'put': 'save', 'delete': 'delete'}), name='adm_save'),
]