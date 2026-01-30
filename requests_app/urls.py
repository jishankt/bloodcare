from django.urls import path
from . import views

app_name = 'request'


urlpatterns = [
    path('send/<int:donor_id>/', views.send, name='send'),
    path('accept/<int:request_id>/', views.accept, name='accept'),
    path('reject/<int:request_id>/', views.reject, name='reject'),
    path('view/<int:request_id>/', views.view_request, name='view_request'),
    path('arrival/<int:request_id>/', views.send_arrival_time, name='send_arrival_time'),
    path('done/<int:request_id>/', views.mark_done, name='mark_done'),
]
