"""
Pogramming task for TJ Ward's application the edLight Senior Fullstack Developer positon
"""

from django.contrib import admin
from .models import Image, Comment

admin.site.register(Image)
admin.site.register(Comment)