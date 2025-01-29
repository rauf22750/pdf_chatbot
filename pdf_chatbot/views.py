import logging
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from accounts.forms import CustomUserCreationForm, PDFUploadForm
from accounts.models import PDFUpload, ChatMessage
from .utils import process_multiple_pdfs
import json
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

logger = logging.getLogger(__name__)

@csrf_exempt
def chat_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_input = data.get('user_input')
        pdf_id = data.get('pdf_id', 'all')
        
        try:
            if pdf_id == 'all':
                pdf_uploads = PDFUpload.objects.all()
                pdf_data = [{'path': pdf.pdf_file.path, 'url': pdf.pdf_file.url} for pdf in pdf_uploads]
            else:
                pdf_upload = PDFUpload.objects.get(id=pdf_id)
                pdf_data = [{'path': pdf_upload.pdf_file.path, 'url': pdf_upload.pdf_file.url}]
            
            chat_history = ChatMessage.objects.filter(user=request.user).order_by('-timestamp')[:5]
            context = "\n".join([f"User: {msg.message}\nAI: {msg.response}" for msg in reversed(chat_history)])
            
            response = process_multiple_pdfs(pdf_data, user_input, context)
            
            ChatMessage.objects.create(
                user=request.user,
                pdf=pdf_upload if pdf_id != 'all' else None,
                message=user_input,
                response=response
            )
            
            return JsonResponse({'response': response})
        except Exception as e:
            logger.error(f"Error in chat_api: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def upload_pdf(request):
    if request.method == 'POST' and request.FILES.get('pdf_file'):
        pdf_file = request.FILES['pdf_file']
        file_name = default_storage.save(f'pdfs/{pdf_file.name}', ContentFile(pdf_file.read()))
        pdf_upload = PDFUpload(pdf_file=file_name, user=request.user)
        pdf_upload.save()
        return JsonResponse({'message': 'PDF uploaded successfully', 'pdf_id': pdf_upload.id})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def chat_view(request):
    pdf_uploads = PDFUpload.objects.filter(user=request.user) if request.user.is_pdf_uploader else PDFUpload.objects.all()
    chat_history = ChatMessage.objects.filter(user=request.user).order_by('timestamp')
    
    return render(request, 'chat/chat.html', {
        'pdf_uploads': pdf_uploads,
        'chat_history': chat_history
    })

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('chat')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})