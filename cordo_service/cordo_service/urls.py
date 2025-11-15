
from django.urls import path, include

urlpatterns = [
    path('api/cordo/', include('cordo.urls')),
]
