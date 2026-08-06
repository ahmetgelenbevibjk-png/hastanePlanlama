from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate

from ..serializers.auth_serializer import RegisterSerializer, LoginSerializer

@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    serializer=RegisterSerializer(data=request.data)
    if serializer.is_validated():
        user=serializer.save();
        token,_=Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'username':user.username,
            'message':'kullanıcı başarıla oluşturuldu.'
        },status=status.HTTP_201_CREATED)
    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    serializer=LoginSerializer(data=request.data)
    if serializer.is_valid():
        username=serializer.validated_data['username']
        password=serializer.validated_data['password']

        user=authenticate(username=username, password=password)
        if user:
            token ,_=Token.objects.get_or_create(user=user)
            return Response({
                'token':token.key,
                'username':user.username
            },status=status.HTTP_200_OK)

        return Response({'detail': 'Hatalı kullanıcı adı veya şişfre.'},status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

