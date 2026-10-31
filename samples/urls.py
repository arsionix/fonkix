from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("catalog/", views.catalog, name="catalog"),
    path("sample/<uuid:pk>/", views.sample_detail, name="sample_detail"),
    path("u/<str:username>/", views.profile, name="profile"),
    path("upload/", views.upload, name="upload"),
]
