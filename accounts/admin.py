from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser, PDFDocument, ChatMessage

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_pdf_uploader', 'is_staff', 'date_joined')
    list_filter = ('is_pdf_uploader', 'is_staff', 'is_superuser', 'date_joined')
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('is_pdf_uploader',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('is_pdf_uploader',)}),
    )
    search_fields = ('username', 'email')
    ordering = ('-date_joined',)

@admin.register(PDFDocument)
class PDFDocumentAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'user', 'uploaded_at', 'pdf_file_link')
    list_filter = ('uploaded_at', 'user')
    search_fields = ('file', 'user__username')
    readonly_fields = ('uploaded_at',)
    date_hierarchy = 'uploaded_at'

    def file_name(self, obj):
        return obj.file.name.split('/')[-1]
    file_name.short_description = 'File Name'

    def pdf_file_link(self, obj):
        if obj.file:
            return format_html('<a href="{}" target="_blank">View PDF</a>', obj.file.url)
        return "No file"
    pdf_file_link.short_description = 'PDF Link'

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'truncated_message', 'truncated_response', 'pdf', 'timestamp')
    list_filter = ('timestamp', 'user')
    search_fields = ('message', 'response', 'user__username')
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'
    raw_id_fields = ('user', 'pdf')

    def truncated_message(self, obj):
        return (obj.message[:75] + '...') if len(obj.message) > 75 else obj.message
    truncated_message.short_description = 'Message'

    def truncated_response(self, obj):
        return (obj.response[:75] + '...') if len(obj.response) > 75 else obj.response
    truncated_response.short_description = 'Response'

    fieldsets = (
        ('User Information', {
            'fields': ('user', 'pdf')
        }),
        ('Chat Content', {
            'fields': ('message', 'response')
        }),
        ('Timestamp', {
            'fields': ('timestamp',),
            'classes': ('collapse',)
        }),
    )

