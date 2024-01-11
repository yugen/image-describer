from django.urls import path
from . import views

urlpatterns = [
    
    path("", views.index, name="index"),
    path("<int:image_id>", views.show, name="image_detail"),
    path("<int:image_id>/comments", views.comments, name="image_comments"),
    path("analyze", views.ingest_image, name="analyze_image"),
]