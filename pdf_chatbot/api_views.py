from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import logging
from .serializers import UserSerializer, PDFDocumentSerializer, ChatMessageSerializer
from accounts.models import ChatMessage
from .utils import generate_response

# Set up logging
logger = logging.getLogger(__name__)

# Login API
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def login_api(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    logger.debug(f"Login attempt for user: {username}")
    
    user = authenticate(username=username, password=password)
    if user:
        token, _ = Token.objects.get_or_create(user=user)
        logger.debug(f"Login successful for user: {username}")
        return Response({
            'token': token.key,
            'user_id': user.id,
            'username': user.username
        }, status=status.HTTP_200_OK)
    
    logger.warning(f"Login failed for user: {username}")
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

# Register API
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def register_api(request):
    logger.debug("Registration attempt with data: %s", request.data)
    
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        logger.debug(f"Registration successful for user: {user.username}")
        return Response({
            'token': token.key,
            'user_id': user.id,
            'username': user.username
        }, status=status.HTTP_201_CREATED)
    
    logger.warning("Registration failed with errors: %s", serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# PDF Upload View
@method_decorator(csrf_exempt, name='dispatch')
class PDFUploadView(generics.CreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = PDFDocumentSerializer

    def perform_create(self, serializer):
        pdf_doc = serializer.save(user=self.request.user)
        # Assuming you have a process_pdf function in utils
        from .utils import process_pdf
        process_pdf(pdf_doc)
        
logger = logging.getLogger(__name__)

class ChatView(generics.CreateAPIView):
    authentication_classes = [TokenAuthentication]  # Ensuring Token Authentication
    permission_classes = [IsAuthenticated]  # Making sure only authenticated users can access
    serializer_class = ChatMessageSerializer

    def create(self, request, *args, **kwargs):
        # Debugging the request headers and token
        logger.debug(f"Request headers: {request.headers}")
        logger.debug(f"Token: {request.auth}")

        # Check if the request contains the message
        message = request.data.get('message')
        if not message:
            return Response({'error': 'Message is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the user is authenticated by checking the request.user
        if not request.user.is_authenticated:
            logger.warning("Unauthorized request - no valid token found.")
            return Response({'error': 'Authentication credentials were not provided.'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            # Generate a response based on the message
            response = generate_response(message, request.user)
            
            # Create a new ChatMessage in the database
            chat_message = ChatMessage.objects.create(
                user=request.user,
                message=message,
                response=response
            )
            
            # Serialize the response and return it
            serializer = self.get_serializer(chat_message)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            # Log any unexpected errors
            logger.error(f"Error in ChatView: {str(e)}")
            return Response({'error': 'An error occurred while processing your request.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)