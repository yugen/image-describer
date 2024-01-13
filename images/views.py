from django.apps import apps
from django.core.paginator import Paginator, EmptyPage
from django.http import JsonResponse, Http404
from rest_framework.decorators import api_view, parser_classes
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import FormParser, MultiPartParser

from .forms import ImageForm, CommentForm
from .models import Image
from .serializers import ImageSerializer, CommentSerializer
from . import actions
import logging

def get_image(image_id: int) -> Image:
    try:
        return Image.objects.get(pk=image_id)
    except Image.DoesNotExist:
        raise Http404("Image does not exist")


@api_view(['GET'])
def index(request):
    """
    Responds with a list of image records
    """
    current_page = request.GET.get('page', 1)
    images = Image.objects.all().order_by('analyzed_at')
    paginator = Paginator(images, apps.get_app_config('images').image_page_size)

    try:
        image_page = ImageSerializer(paginator.page(current_page), many=True)
        return JsonResponse({
                'data': image_page.data,
                'num_pages': paginator.num_pages,
                'current_page': current_page
            }
        )
    except EmptyPage:
        return JsonResponse({"error": 'The page is empty', 'num_pages': paginator.num_pages}, status=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE)

@api_view(['POST'])
@parser_classes([FormParser, MultiPartParser])
def ingest_image(request):
    serializer = ImageSerializer(data=request.data)
    if not serializer.is_valid():
        return JsonResponse({'errors': serializer.errors}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    imageModel = Image(file=request.data['file'])
    imageModel.save()
    logging.debug(f"stored image at {imageModel.file.path} for Image {imageModel.id}")

    imageModel = actions.analyze_image(imageModel)
    return Response(ImageSerializer(imageModel).data)

@api_view(['GET'])
def show(request, image_id):
    image = get_image(image_id)
    
    return JsonResponse(ImageSerializer(image).data)

@api_view(['GET'])
def show_with_comments(request, image_id):
    image = get_image(image_id)
    try:
        comment_page = actions.get_paginated_comments(image, current_page=int(request.GET.get('comment_page', 1)))
    except EmptyPage as e:
        return JsonResponse({"error": 'The page of comments you requested is empty', 'num_pages': e.num_pages}, status=416)
    
    data = ImageSerializer(image).data
    data['comments'] = comment_page
   
    return JsonResponse(data)
    
@api_view(['GET', 'POST'])
def comments(request, image_id):
    
    """
    Retrieve a page of comments for an image OR create a comment for an image
    """
    image = get_image(image_id)

    if request.method == "GET":
        current_page = int(request.GET.get('page', 1))

        try:
            data = actions.get_paginated_comments(image, current_page)
            return JsonResponse(data)
        except EmptyPage as e:
            return JsonResponse({"error": 'The page is empty', 'num_pages': e.num_pages}, status=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE)
        
    if request.method == "POST":
        form = CommentForm(request.data)
        if not form.is_valid():
            return JsonResponse({'errors': form.errors}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        
        comment = image.comment_set.create(content=form.clean()['content'])
        try:
            serializer = CommentSerializer(comment)
            return Response(serializer.data)
        except Exception as e:
            return Response(str(e), 400)
