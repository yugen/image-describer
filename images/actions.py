"""
Pogramming task for TJ Ward's application the edLight Senior Fullstack Developer positon
"""

from .forms import ImageForm, CommentForm
from .models import Image, Comment
from datetime import datetime
from .describers import make_image_describer
from .serializers import CommentSerializer
from django.core.paginator import Paginator, EmptyPage
from django.apps import apps
from django.http import Http404
import logging

def store_and_analyze_image(form: ImageForm) -> Image:
    imageModel = form.save()
    imageModel = analyze_image(imageModel)

    return imageModel

def analyze_image(image: Image) -> Image:
    """
    Uses a "describer" to get the a description.
    If None is returned analysis was unsuccessful and the image has not yet been analyzed.
    """ 
    logging.debug('actions.analyze_image')
    describer = make_image_describer()
    logging.debug(f'using describer: {describer}')
    try:
        description = describer.describe_image(image.file.path)
        image.description = description
        image.analyzed_at = datetime.now()
        image.save()
        logging.debug('analyzed image')
    except Exception as e:
        logging.warn(e)
        pass
    
    return image

def get_paginated_comments(image: Image, current_page: int=1) -> dict:
    try:
        comments = image.comment_set.all().order_by('created_at')
        paginator = Paginator(comments, apps.get_app_config('images').comment_page_size)
        comment_page = CommentSerializer(paginator.page(current_page), many=True)
        return {
            'data': comment_page.data,
            'num_pages': paginator.num_pages,
            'current_page': current_page
        }
    except EmptyPage as e:
        e.num_pages = paginator.num_pages
        raise e

def add_comment(image: Image, form: CommentForm) -> Comment:
    comment = form.save()

    return comment