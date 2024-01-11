from django.db import models

class Image(models.Model):
    # Model representing an image record.

    file = models.ImageField(upload_to='images')
    description = models.JSONField(null=True, blank=True)
    analyzed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    @property
    def analyzed(self) -> bool:
        return self.analyzed_at != None

class Comment(models.Model):
    # Model representing a comment.

    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
