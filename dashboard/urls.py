from django.contrib import admin
from django.urls import path,include
from .views import *


urlpatterns = [
    path('',index, name='dash'),
    path('login/',login, name='login'),
    path('logout/',logout_view, name='logout'),
    path('signup/',signup, name='signup'),
    path('profile/', profile_view, name='profile'),
    path('post/', post_blog, name='post_blog'),
    path('post/delete/<int:post_id>/', delete_post, name='delete_post'),
    path('post/update/', update_post, name='update_post'),

    path('book/', book_appointment, name='book_appointment'),
    # path('update-appointment/', update_appointment, name='update_appointment'),
    # path('confirm/<int:appointment_id>/', views.confirm_appointment, name='confirm_appointment'),
    # path('doctors/', views.doctor_list, name='doctor_list'),
]