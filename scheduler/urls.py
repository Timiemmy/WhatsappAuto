from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.index, name='index'),
    path('view_scheduled/', views.view_scheduled, name='view_scheduled'),
    path('update_scheduled/<int:id>/',
         views.update_scheduled, name='update_scheduled'),
    path('delete_scheduled/<int:id>/',
         views.delete_scheduled, name='delete_scheduled'),
    path('account/', views.account, name='account'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('password_reset/', views.CustomPasswordResetView.as_view(),
         name='password_reset'),
    path('password_reset/done/', views.CustomPasswordResetDoneView.as_view(),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('reset/done/', views.CustomPasswordResetCompleteView.as_view(),
         name='password_reset_complete'),
]
