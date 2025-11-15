
from django.urls import path, include

urlpatterns = [
   
    path('api/finance/', include('finance.urls')),
]
