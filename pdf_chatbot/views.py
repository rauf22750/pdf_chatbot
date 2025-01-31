import logging
import os
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from accounts.forms import CustomUserCreationForm, PDFUploadForm, ChatForm
from accounts.models import PDFDocument, ChatMessage
from .utils import process_pdf, generate_response

logger = logging.getLogger(__name__)

@login_required
@require_http_methods(["GET", "POST"])
def chat_view(request):
    pdfs = PDFDocument.objects.filter(user=request.user)
    chat_history = ChatMessage.objects.filter(user=request.user)
    
    if request.method == 'POST':
        if 'file' in request.FILES:
            pdf_form = PDFUploadForm(request.POST, request.FILES)
            if pdf_form.is_valid():
                pdf_doc = pdf_form.save(commit=False)
                pdf_doc.user = request.user
                pdf_doc.save()
                try:
                    logger.info(f"Processing uploaded PDF: {pdf_doc.file.path}")  # Correct file path
                    process_pdf(pdf_doc)
                    return JsonResponse({
                        'message': 'PDF processed successfully',
                        'pdf_id': pdf_doc.id,
                        'pdf_name': pdf_doc.file.name,
                        'pdf_url': pdf_doc.file.url
                    })
                except Exception as e:
                    logger.error(f"Error processing PDF: {str(e)}")
                    pdf_doc.delete()
                    return JsonResponse({'error': str(e)}, status=500)
            else:
                return JsonResponse({'error': 'Invalid form data'}, status=400)
        else:
            chat_form = ChatForm(request.POST)
            if chat_form.is_valid():
                message = chat_form.cleaned_data['message']
                try:
                    logger.info(f"Generating response for message: {message}")
                    response = generate_response(message, request.user)
                    chat_message = ChatMessage.objects.create(
                        user=request.user,
                        message=message,
                        response=response
                    )
                    return JsonResponse({
                        'response': response,
                        'timestamp': chat_message.timestamp.isoformat()
                    })
                except Exception as e:
                    logger.error(f"Error generating response: {str(e)}")
                    return JsonResponse({'error': str(e)}, status=500)
            else:
                return JsonResponse({'error': 'Invalid form data'}, status=400)
    
    return render(request, 'chat/chat.html', {
        'pdfs': pdfs,
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
