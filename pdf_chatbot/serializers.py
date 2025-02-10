from rest_framework import serializers
from accounts.models import CustomUser, PDFDocument, ChatMessage

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': False}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user

class PDFDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PDFDocument
        fields = ['id', 'user', 'file', 'timestamp']

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'user', 'message', 'response', 'timestamp', 'pdf']
