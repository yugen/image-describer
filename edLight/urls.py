"""
Pogramming task for TJ Ward's application the edLight Senior Fullstack Developer positon
"""

from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from images import views as images_views

urlpatterns = [
    path('', RedirectView.as_view(url='images/')),
    path('admin/', admin.site.urls),
    path('images/', images_views.index, name="image_list"),
    path('analyze-image', images_views.ingest_image, name="analize-image"),
    # path('images/', include("images.urls")),
    path('image/<int:image_id>', images_views.show_with_comments, name="image_detail"),
    path('image/<int:image_id>/comments', images_views.comments, name="add_comment"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
