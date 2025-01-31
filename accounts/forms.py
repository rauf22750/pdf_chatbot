from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import CustomUser, PDFDocument

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    is_pdf_uploader = forms.BooleanField(
        required=False,
        initial=True,
        help_text="Check this if you want to upload PDFs."
    )

    class Meta:
        model = CustomUser
        fields = ("username", "email", "password1", "password2", "is_pdf_uploader")

    def clean_email(self):
        email = self.cleaned_data['email']
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("This email address is already in use.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.is_pdf_uploader = self.cleaned_data["is_pdf_uploader"]
        if commit:
            user.save()
        return user

class PDFUploadForm(forms.ModelForm):
    class Meta:
        model = PDFDocument
        fields = ['file']
        widgets = {
            'file': forms.FileInput(attrs={'accept': 'application/pdf'})
        }

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            if not file.name.endswith('.pdf'):
                raise ValidationError("Only PDF files are allowed.")
            if file.size > 50 * 1024 * 1024:  # 50 MB limit
                raise ValidationError("File size cannot exceed 10 MB.")
        return file

class ChatForm(forms.Form):
    message = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Type your message here...'}),
        max_length=1000,
        required=True
    )

