from django.urls import path, include

urlpatterns = [
    path('v1/', include("shop.api_v1_urls")),
]
