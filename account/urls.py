from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('api/auth/set_permission/<str:ressource>', views.AccountView.as_view({'put': 'set_permission'}), name='auth_set_permission'),
    path('api/auth/set_profil/<str:ressource>', views.AccountView.as_view({'put': 'set_profil'}), name='auth_set_profil'),

    path('auth/<str:ressource>/', views.AccountView.as_view({'get': 'index'}), name='auth_index'),  
    path('auth/<str:ressource>/<int:id>/', views.AccountView.as_view({'get': 'display'}), name='auth_display'),
    path('api/auth/many/<str:ressource>/', views.AccountView.as_view({'get': 'get_many'}), name='auth_get_many'),
    path('api/auth/one/<str:ressource>/', views.AccountView.as_view({'get': 'get_one'}), name='auth_get_one'),
    path('api/auth/<str:ressource>', views.AccountView.as_view({'post': 'store'}), name='auth_store'),
    path('api/auth/<str:ressource>/<int:id>', views.AccountView.as_view({'put': 'save', 'delete': 'delete'}), name='auth_save'),
]