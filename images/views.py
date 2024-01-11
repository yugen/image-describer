from django.apps import apps
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, EmptyPage
from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST, require_http_methods

from images.forms import ImageForm, CommentForm
from images.models import Image
from images.serializers import ImageSerializer, CommentSerializer
from images import actions

@require_GET
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
        return JsonResponse({"error": 'The page is empty', 'num_pages': paginator.num_pages}, status=416)


@require_POST
def ingest_image(request):
    form = ImageForm(request.POST, request.FILES)
    if not form.is_valid():
        return JsonResponse({'errors': form.errors}, status=422)
    
    imageModel = actions.store_and_analyze_image(form)
    return JsonResponse({"image": ImageSerializer(imageModel).data})

@require_GET
def show(request, image_id):
    try:
        image = Image.objects.get(pk=image_id)
    except Image.DoesNotExist:
        raise Http404("Image does not exist")
    return JsonResponse(ImageSerializer(image).data)

@require_http_methods(['GET', 'POST'])
def comments(request, image_id):
    try:
        image = Image.objects.get(pk=image_id)
    except Image.DoesNotExist:
        raise Http404("Image does not exist")

    if request.method == "GET":
        current_page = int(request.GET.get('page', 1))

        try:
            comments = image.comment_set.all().order_by('created_at')
            paginator = Paginator(comments, apps.get_app_config('images').comment_page_size)
            comment_page = CommentSerializer(paginator.page(current_page), many=True)
            return JsonResponse({
                    'data': comment_page.data,
                    'num_pages': paginator.num_pages,
                    'current_page': current_page
                }
            )
        except EmptyPage:
            return JsonResponse({"error": 'The page is empty', 'num_pages': paginator.num_pages}, status=416)
        
    if request.method == "POST":
        form = CommentForm(request.POST)
        if not form.is_valid():
            return JsonResponse({'errors': form.errors}, status=422)

        comment = image.comment_set.create(content=form.clean()['content'])
        return JsonResponse(CommentSerializer(comment).data)