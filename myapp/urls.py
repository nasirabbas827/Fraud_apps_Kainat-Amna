from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('update_profile/', views.update_profile, name='update_profile'),
    path('app/<int:app_id>/', views.app_details, name='app_details'),
    path('feedback/submit/', views.submit_feedback, name='submit_feedback'),
    path('feedback/list/', views.feedback_list, name='feedback_list'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
