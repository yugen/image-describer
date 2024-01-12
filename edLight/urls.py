"""
URL configuration for edLight project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
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
    path('analyze_image', images_views.ingest_image),
    path('image/<int:image_id>', images_views.show_with_comments),
    path('images/', include("images.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
