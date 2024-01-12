from .forms import ImageForm, CommentForm
from .models import Image, Comment
from datetime import datetime
from .describers import make_image_describer

def store_and_analyze_image(form: ImageForm) -> Image:
    imageModel = form.save()
    imageModel = analyze_image(imageModel)

    return imageModel

def analyze_image(image: Image) -> Image:
    """
    Uses a "describer" to get the a description.
    If None is returned analysis was unsuccessful and the image has not yet been analyzed.
    """ 
    describer = make_image_describer()
    try:
        description = describer.describe_image(image.file.path)
        image.description = description
        image.analyzed_at = datetime.now()
        image.save()
    except:
        # log exception
        pass
    
    return image

def add_comment(image: Image, form: CommentForm) -> Comment:
    comment = form.save()

    return comment