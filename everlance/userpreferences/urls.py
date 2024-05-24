from . import views
from django.urls import path

urlpatterns = [
    path('', views.index, name="preferences"),
    path('account',views.account,name="account"),
    path('reset-password',views.reset_password,name='reset-password'),
    path('delete-account',views.delete_account,name='delete-account')
]
