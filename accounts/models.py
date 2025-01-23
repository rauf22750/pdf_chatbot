from django.contrib.auth.models import AbstractUser
from django.db import models
import os

class CustomUser(AbstractUser):
    is_pdf_uploader = models.BooleanField(default=False)

    def __str__(self):
        return self.username

class PDFUpload(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    pdf_file = models.FileField(upload_to='pdfs/')
    original_name = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.original_name}"

    def delete(self, *args, **kwargs):
        # Delete the file from storage when the model instance is deleted
        if self.pdf_file and os.path.isfile(self.pdf_file.path):
            os.remove(self.pdf_file.path)
        super().delete(*args, **kwargs)

class ChatMessage(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    pdf = models.ForeignKey(PDFUpload, on_delete=models.SET_NULL, null=True, blank=True)
    message = models.TextField()
    response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.timestamp}"

    class Meta:
        ordering = ['-timestamp']