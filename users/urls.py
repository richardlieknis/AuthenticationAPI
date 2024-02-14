from django.urls import path, include
from .views import RegisterView, LoginView, UserView, LogoutView, ResetPassword, CompleteResetPassword

urlpatterns = [
    path('register', RegisterView.as_view()),
    path('login', LoginView.as_view()),
    path('user', UserView.as_view()),
    path('logout', LogoutView.as_view()),
    path('reset-password', ResetPassword.as_view()),
    path('complete-reset-password/<str:token>/',
         CompleteResetPassword.as_view()),
]
