from django.apps import apps
from django.core.paginator import Paginator, EmptyPage
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_GET, require_POST, require_http_methods

from .forms import ImageForm, CommentForm
from .models import Image
from .serializers import ImageSerializer, CommentSerializer
from . import actions

def get_image(image_id: int) -> Image:
    try:
        return Image.objects.get(pk=image_id)
    except Image.DoesNotExist:
        raise Http404("Image does not exist")


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
    image = get_image(image_id)
    
    return JsonResponse(ImageSerializer(image).data)

@require_GET
def show_with_comments(request, image_id):
    image = get_image(image_id)
    try:
        comment_page = actions.get_paginated_comments(image, current_page=int(request.GET.get('comment_page', 1)))
    except EmptyPage as e:
        return JsonResponse({"error": 'The page of comments you requested is empty', 'num_pages': e.num_pages}, status=416)
    
    data = ImageSerializer(image).data
    data['comments'] = comment_page
   
    return JsonResponse(data)
    
@require_http_methods(['GET', 'POST'])
def comments(request, image_id):
    image = get_image(image_id)

    if request.method == "GET":
        current_page = int(request.GET.get('page', 1))

        try:
            data = actions.get_paginated_comments(image, current_page)
            return JsonResponse(data)
        except EmptyPage as e:
            return JsonResponse({"error": 'The page is empty', 'num_pages': e.num_pages}, status=416)
        
    if request.method == "POST":
        form = CommentForm(request.POST)
        if not form.is_valid():
            return JsonResponse({'errors': form.errors}, status=422)

        comment = image.comment_set.create(content=form.clean()['content'])
        return JsonResponse(CommentSerializer(comment).data)