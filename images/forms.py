from django.forms import ModelForm
from images.models import Image, Comment

class ImageForm(ModelForm):
    class Meta:
        model = Image
        fields = '__all__'

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['content']