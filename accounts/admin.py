from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, PDFUpload, ChatMessage

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'is_staff', 'is_pdf_uploader']
    list_filter = ['is_staff', 'is_superuser', 'is_pdf_uploader']
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('is_pdf_uploader',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('is_pdf_uploader',)}),
    )

class PDFUploadAdmin(admin.ModelAdmin):
    list_display = ['user', 'original_name', 'uploaded_at']
    list_filter = ['uploaded_at', 'user']
    search_fields = ['user__username', 'original_name']
    date_hierarchy = 'uploaded_at'

class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['user', 'pdf', 'short_message', 'timestamp']
    list_filter = ['timestamp', 'user']
    search_fields = ['user__username', 'message', 'response']
    date_hierarchy = 'timestamp'

    def short_message(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    short_message.short_description = 'Message'

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(PDFUpload, PDFUploadAdmin)
admin.site.register(ChatMessage, ChatMessageAdmin)