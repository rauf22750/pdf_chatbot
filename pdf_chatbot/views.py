import logging
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from accounts.models import CustomUser, PDFDocument, ChatMessage
from .utils import process_pdf, generate_response
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)

# Login view without forms.py
@ensure_csrf_cookie
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not username or not password:
            return render(request, 'registration/login.html', {'error': 'Username and password are required'})

        # Attempt to authenticate user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('chat')
        else:
            return render(request, 'registration/login.html', {'error': 'Invalid credentials'})

    return render(request, 'registration/login.html')

# Register view without forms.py
@ensure_csrf_cookie
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        email = request.POST.get('email')
        
        if not username or not password or not email or not password_confirm:
            return render(request, 'registration/register.html', {'error': 'All fields are required'})

        if password != password_confirm:
            return render(request, 'registration/register.html', {'error': 'Passwords do not match'})

        # Email validation
        try:
            validate_email(email)
        except ValidationError:
            return render(request, 'registration/register.html', {'error': 'Invalid email address'})

        # Check if the user already exists
        if CustomUser.objects.filter(username=username).exists():
            return render(request, 'registration/register.html', {'error': 'Username already taken'})

        if CustomUser.objects.filter(email=email).exists():
            return render(request, 'registration/register.html', {'error': 'Email already registered'})

        try:
            user = CustomUser.objects.create_user(username=username, password=password, email=email)
            login(request, user)
            return redirect('chat')
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            return render(request, 'registration/register.html', {'error': 'An error occurred. Please try again'})

    return render(request, 'registration/register.html')

# Chat view (with PDF upload and chat history)
@login_required
@require_http_methods(["GET", "POST"])
@csrf_exempt
def chat_view(request):
    pdfs = PDFDocument.objects.filter(user=request.user)
    chat_history = ChatMessage.objects.filter(user=request.user)

    if request.method == 'POST':
        if 'file' in request.FILES:
            pdf = request.FILES['file']
            try:
                # logger.info(f"Processing uploaded PDF: {pdf.name}")
                pdf_doc = PDFDocument.objects.create(user=request.user, file=pdf)
                process_pdf(pdf_doc)  # Assuming process_pdf handles PDF processing
                return JsonResponse({
                    'message': 'PDF processed successfully',
                    'pdf_id': pdf_doc.id,
                    'pdf_name': pdf_doc.file.name,
                    'pdf_url': pdf_doc.file.url
                })
            except Exception as e:
                # logger.error(f"Error processing PDF: {str(e)}")
                return JsonResponse({'error': str(e)}, status=500)
        else:
            message = request.POST.get('message')
            pdf_id = request.POST.get('pdf_id')  # Assuming PDF ID is passed with the message
            
            try:
                pdf_doc = PDFDocument.objects.get(id=pdf_id) if pdf_id else None
                # logger.info(f"Generating response for message: {message}")
                response = generate_response(message, request.user)
                chat_message = ChatMessage.objects.create(
                    user=request.user,
                    message=message,
                    response=response,
                    pdf=pdf_doc  # Link the response to the PDF (if applicable)
                )
                return JsonResponse({
                    'response': response,
                    'timestamp': chat_message.timestamp.isoformat()
                })
            except Exception as e:
                # logger.error(f"Error generating response: {str(e)}")
                return JsonResponse({'error': str(e)}, status=500)

    return render(request, 'chat/chat.html', {
        'pdfs': pdfs,
        'chat_history': chat_history
    })

# Logout view to handle user logout
@login_required
def logout_view(request):
    logout(request)
    return redirect('login')
