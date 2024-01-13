"""
Pogramming task for TJ Ward's application the edLight Senior Fullstack Developer positon
"""

from django.apps import apps
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage
from django.http import JsonResponse, Http404
from rest_framework.decorators import api_view, parser_classes
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from drf_spectacular.types import OpenApiTypes

from .forms import ImageForm, CommentForm
from .models import Image
from . import serializers
from . import actions
import logging
from .describers import ImageDescriberError

@extend_schema(
     description='Returns a page (10) image records at a time.',
     responses=serializers.ImageSerializer(many=True),
     parameters=[
        OpenApiParameter("page", OpenApiTypes.NUMBER, OpenApiParameter.QUERY),
     ]
)
@api_view(['GET'])
def index(request):
    """
    Responds with a list of image records
    """
    current_page = request.GET.get('page', 1)
    images = Image.objects.all().order_by('analyzed_at')
    paginator = Paginator(images, apps.get_app_config('images').image_page_size)

    try:
        image_page = serializers.ImageSerializer(paginator.page(current_page), many=True)
        return JsonResponse({
                'data': image_page.data,
                'num_pages': paginator.num_pages,
                'current_page': current_page
            }
        )
    except EmptyPage:
        return JsonResponse({"error": 'The page is empty', 'num_pages': paginator.num_pages}, status=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE)

@extend_schema(
    description='Ingest a new image.  Stores an image model and analyze the image',
    responses={
        200: serializers.ImageSerializer,
        (207, "application/json"): {
            "description": "Image stored, but analysis failed",
            "type": "object",
            "properties": {
                "id": { "type": "integer" },
                "file": { "type": "integer" },
                "analyzed": { "type": "boolean" },
                "description": { "type": "string" },
                "errors": {
                    "type": "object",
                    "properties": {
                        "describer": { "type": "array", "items": { "type": "string"}}
                    }
                },
            }
        },
        422: OpenApiResponse(description='Bad request response includes errors'),
    },
    request={
        'multipart/form-data': {
            'type': 'object',
            'properties': {
                'file': {
                'type': 'string',
                'format': 'binary'
                }
            }
        }
    },
)
@api_view(['POST'])
def ingest_image(request):
    """
    Ingest a new image.  Store an image model and analyze the image
    """
    serializer = serializers.ImageUploadSerializer(data=request.data)
    if not serializer.is_valid():
        return JsonResponse({'errors': serializer.errors}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    imageModel = Image(file=request.data['file'])
    imageModel.save()
    logging.debug(f"stored image at {imageModel.file.path} for Image {imageModel.id}")

    status_code = status.HTTP_200_OK
    response_data = serializers.ImageSerializer(imageModel).data
    try:
        logging.debug('try to analyze_image')
        imageModel = actions.analyze_image(imageModel)
    except Exception as e:
        logging.debug(str(e))
        status_code = status.HTTP_207_MULTI_STATUS
        response_data['errors'] = {'describer': [str(e)]}
        
    return Response(response_data, status_code)

@extend_schema(
     description='Returns an image record without comments.',
     responses=serializers.ImageSerializer,
)
@api_view(['GET'])
def show(request, image_id):
    """
    Get an image record
    """
    image = get_object_or_404(Image, pk=image_id)
    
    return JsonResponse(serializers.ImageSerializer(image).data)

@extend_schema(
    responses = {
        (200, "application/json"): {
            "description": "Success",
            "type": "object",
            "properties": {
                "id": {
                    "type": "integer",
                    "minLength": 1
                },
                "file": {
                    "type": "string",
                    "minLength": 1
                },
                "description": { "type": "string" },
                "analyzed": { "type": "boolean" },
                "comments": {
                    "type": "object",
                    "properties": {
                        "num_pages": { "type": "integer" },
                        "current_page": { "type": "integer" },
                        "data": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": { "type": "integer"},
                                    "content": { "type": "string"},
                                    "created_at": { "type": "string"},
                                }
                            }
                        }
                    }
                }
            },
            "required": [
                "id",
                "file",
                "analyzed"
            ]
        },
    },
    parameters = [
        OpenApiParameter('comment_page', OpenApiTypes.NUMBER, OpenApiParameter.QUERY)
    ]
)
@api_view(['GET'])
def show_with_comments(request, image_id):
    """
    Get an image record with a page of comments
    """
    image = get_object_or_404(Image, pk=image_id)
    try:
        comment_page = actions.get_paginated_comments(image, current_page=int(request.GET.get('comment_page', 1)))
    except EmptyPage as e:
        return JsonResponse({"error": 'The page of comments you requested is empty', 'num_pages': e.num_pages}, status=416)
    
    data = serializers.ImageSerializer(image).data
    data['comments'] = comment_page
   
    return JsonResponse(data)
    
@extend_schema(
    description='Ingest a new image.  Stores an image model and analyze the image',
    responses={
        200: serializers.CommentSerializer,
        422: OpenApiResponse(description='Bad request response includes errors')
    },
    request=serializers.CommentCreateSerializer,
)
@api_view(['POST'])
def comments(request, image_id):
    """
    Retrieve a page of comments for an image OR create a comment for an image
    """
    image = get_object_or_404(Image, pk=image_id)

    # form = CommentForm(request.data)
    input_serializer = serializers.CommentCreateSerializer(data=request.data)
    if not input_serializer.is_valid():
        return JsonResponse({'errors': input_serializer.errors}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    
    comment = image.comment_set.create(content=input_serializer.data['content'])
    try:
        serializer = serializers.CommentSerializer(comment)
        return Response(serializer.data)
    except Exception as e:
        return Response(str(e), 400)
