from .forms import ImageForm, CommentForm
from .models import Image, Comment
from datetime import datetime

def store_and_analyze_image(form: ImageForm) -> Image:
    imageModel = form.save()
    imageModel = analyze_image(imageModel)

    return imageModel

def analyze_image(image: Image) -> Image:
    image.description = {'a': 'Some description'}
    image.analyzed_at = datetime.now()

    image.save()

    return image

def add_comment(image: Image, form: CommentForm) -> Comment:
    comment = form.save()

    return comment