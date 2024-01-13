from rest_framework import serializers
from images.models import Image, Comment

class ImageUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['file']

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'file', 'description', 'analyzed']
        
class CommentCreate(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['content']
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'content', 'image_id', 'created_at']
