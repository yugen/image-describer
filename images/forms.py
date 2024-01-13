from django.forms import ModelForm
from images.models import Image, Comment

class ImageForm(ModelForm):
    class Meta:
        model = Image
        fields = ['file']

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['content']