from django.urls import path
from .views import LoginView, LogoutView, CallbackView, AdminView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('callback/', CallbackView.as_view(), name='callback'),
    path('admin/', AdminView.as_view(), name='admin'),
]
