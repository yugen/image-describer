"""
Pogramming task for TJ Ward's application the edLight Senior Fullstack Developer positon
"""

from django.apps import AppConfig
import os
class ImagesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'images'
    image_page_size = 10
    comment_page_size = 10
    openai_api_key=os.getenv('OPENAI_API_KEY')