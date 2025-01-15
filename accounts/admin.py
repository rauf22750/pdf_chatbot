from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, PDFUpload, ChatMessage

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'is_pdf_uploader', 'is_staff']
    fieldsets = UserAdmin.fieldsets + ((None, {'fields': ('is_pdf_uploader',)}),)
    add_fieldsets = UserAdmin.add_fieldsets + ((None, {'fields': ('is_pdf_uploader',)}),)

class PDFUploadAdmin(admin.ModelAdmin):
    list_display = ['user', 'pdf_file', 'uploaded_at']
    list_filter = ['user', 'uploaded_at']
    search_fields = ['user__username', 'pdf_file']

class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['user', 'pdf', 'message', 'timestamp']
    list_filter = ['user', 'pdf', 'timestamp']
    search_fields = ['user__username', 'message', 'response']

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(PDFUpload, PDFUploadAdmin)
admin.site.register(ChatMessage, ChatMessageAdmin)

