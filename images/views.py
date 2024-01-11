from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, Http404
from django.views.decorators.http import require_GET, require_POST
from images.models import Image, Comment
from images.serializers import ImageSerializer, CommentSerializer
from images.forms import ImageForm
from images import actions

@require_GET
def index(request):
    # Responds with a list of image records
    
    # TODO: paginate
    images = ImageSerializer(Image.objects.all(), many=True)
    return JsonResponse(images.data, safe=False)

@require_POST
def ingest_image(request):
    form = ImageForm(request.POST, request.FILES)
    if not form.is_valid():
        return JsonResponse(form.errors, status=422)
    
    imageModel = actions.store_and_analyze_image(form)
    return JsonResponse({"image": ImageSerializer(imageModel).data})

@require_GET
def show(request, image_id):
    try:
        image = Image.objects.get(pk=image_id)
    except Image.DoesNotExist:
        raise Http404("Image does not exist")
    return JsonResponse(ImageSerializer(image).data)

@require_GET
def comments(request, image_id):
    try:
        image = Image.objects.get(pk=image_id)
        # TODO: Paginate
        comments = CommentSerializer(image.comment_set, many=True)
        return JsonResponse(comments.data, safe=False)
    except Image.DoesNotExist:
        raise Http404("Imge does not exist")
    
@require_POST
def add_comment(request, image_id):
    return HttpResponse(f"add comment")