import logging
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from accounts.forms import CustomUserCreationForm, PDFUploadForm
from accounts.models import PDFUpload, ChatMessage
from .utils import process_multiple_pdfs

logger = logging.getLogger(__name__)

from django.http import HttpResponse


@login_required
def chat_view(request):
    pdf_uploads = PDFUpload.objects.filter(user=request.user) if request.user.is_pdf_uploader else PDFUpload.objects.all()
    chat_history = ChatMessage.objects.filter(user=request.user).order_by('timestamp')
    
    if request.method == 'POST':
        if request.user.is_pdf_uploader and 'pdf_file' in request.FILES:
            form = PDFUploadForm(request.POST, request.FILES)
            if form.is_valid():
                pdf_upload = form.save(commit=False)
                pdf_upload.user = request.user
                pdf_upload.save()
                return redirect('chat')
        else:
            pdf_id = request.POST.get('pdf_id')
            user_input = request.POST.get('user_input')
            
            if user_input:
                try:
                    if pdf_id == 'all':
                        pdf_data = [{'path': pdf.pdf_file.path, 'url': pdf.pdf_file.url} for pdf in pdf_uploads]
                        pdf_upload = None
                    else:
                        pdf_upload = PDFUpload.objects.get(id=pdf_id)
                        pdf_data = [{'path': pdf_upload.pdf_file.path, 'url': pdf_upload.pdf_file.url}]
                    
                    # Get only the last message for context
                    last_message = chat_history.last()
                    context = f"User: {last_message.message}\nAI: {last_message.response}" if last_message else ""
                    
                    response = process_multiple_pdfs(pdf_data, user_input, context)
                    logger.info(f"Processed PDF(s). Response length: {len(response)}")
                    
                    ChatMessage.objects.create(
                        user=request.user,
                        pdf=pdf_upload,
                        message=user_input,
                        response=response
                    )
                    
                    return JsonResponse({'response': response})
                except Exception as e:
                    logger.error(f"Error in chat_view: {str(e)}")
                    return JsonResponse({'error': str(e)}, status=500)
            else:
                return JsonResponse({'error': 'Missing user_input'}, status=400)
    
    form = PDFUploadForm() if request.user.is_pdf_uploader else None
    
    return render(request, 'chat/chat.html', {
        'form': form,
        'pdf_uploads': pdf_uploads,
        'chat_history': chat_history
    })

@ensure_csrf_cookie
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

