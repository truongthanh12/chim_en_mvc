
from . import views

from django.urls import path, include
from django.conf.urls import url
from accounts.API.apis import RegisterAPI, LoginAPI, UserAPI
urlpatterns = [
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('user-payments/', views.user_payments, name='user-payments'),
    path('user-payments/<int:id>', views.user_payment, name='user-payment'),

    path('logout/', views.logout, name='logout'),
    path('profile/', views.profile, name='profile'),

    path('changePassword/', views.changePassword, name='change-password'),
    path('changeEmail/', views.change_email, name='change-email'),


    # path('payment/', views.userPayments, name='user_payments'),
    # path('payment/<int:id>', views.userPayment, name='user_payment'),

    path('activate/<str:uidb64>/<str:token>',
         views.activate, name='activate'),
    path('change-email/<int:user>',
         views.verify_change_email, name='verify_change_email'),

]
