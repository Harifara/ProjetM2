from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/rh/', include('rh.urls')),  # 🔥 Inclut toutes les routes du module RH
]
