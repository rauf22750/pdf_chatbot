import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from accounts.models import CustomUser, PDFDocument, ChatMessage
from .utils import process_pdf, generate_response
from django.http import JsonResponse

logger = logging.getLogger(__name__)

# 📌 **User Login API**
@api_view(['POST'])
def login_api(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        logger.error("Login failed: Missing username or password")
        return Response({'error': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(request, username=username, password=password)
    if user:
        login(request, user)
        token, _ = Token.objects.get_or_create(user=user)  # Generate token
        return Response({'message': 'Login successful', 'token': token.key}, status=status.HTTP_200_OK)
    
    logger.error(f"Login failed: Invalid credentials for username: {username}")
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

# 📌 **User Registration API**
@api_view(['POST'])
def register_api(request):
    username = request.data.get('username')
    password = request.data.get('password')
    password_confirm = request.data.get('password_confirm')
    email = request.data.get('email')

    if not username or not password or not email or not password_confirm:
        return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)

    if password != password_confirm:
        return Response({'error': 'Passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        validate_email(email)
    except ValidationError:
        return Response({'error': 'Invalid email address'}, status=status.HTTP_400_BAD_REQUEST)

    if CustomUser.objects.filter(username=username).exists():
        return Response({'error': 'Username already taken'}, status=status.HTTP_400_BAD_REQUEST)

    if CustomUser.objects.filter(email=email).exists():
        return Response({'error': 'Email already registered'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = CustomUser.objects.create_user(username=username, password=password, email=email)
        token = Token.objects.create(user=user)  # Generate authentication token
        return Response({'message': 'Registration successful', 'token': token.key}, status=status.HTTP_201_CREATED)
    except Exception as e:
        logger.error(f"Error during registration: {str(e)}")
        return Response({'error': 'An error occurred. Please try again'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 📌 **Chat API (Send Message & Get Chat History)**
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def chat_api(request):
    if request.method == 'POST':
        message = request.data.get('message')

        if not message:
            return Response({'error': 'Message is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            response = generate_response(message, request.user)
            chat_message = ChatMessage.objects.create(user=request.user, message=message, response=response)

            return Response({'response': response, 'timestamp': chat_message.timestamp.isoformat()}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Chat error: {str(e)}")
            return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    elif request.method == 'GET':
        chat_history = ChatMessage.objects.filter(user=request.user).order_by('-timestamp')
        chat_data = [{'message': chat.message, 'response': chat.response, 'timestamp': chat.timestamp.isoformat()} for chat in chat_history]

        return Response({'chat_history': chat_data}, status=status.HTTP_200_OK)

# 📌 **PDF Upload API**
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_pdf(request):
    if 'file' not in request.FILES:
        return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

    pdf_file = request.FILES['file']
    
    try:
        pdf_doc = PDFDocument.objects.create(user=request.user, file=pdf_file)
        process_pdf(pdf_doc)  # Process PDF (Extract text, generate vectors, etc.)

        return Response({
            'message': 'PDF uploaded successfully!',
            'pdf_id': pdf_doc.id,
            'pdf_name': pdf_doc.file.name,
            'pdf_url': pdf_doc.file.url
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        logger.error(f"Error uploading PDF: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 📌 **User Logout API**
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_api(request):
    request.user.auth_token.delete()  # Remove authentication token
    logout(request)
    return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)
