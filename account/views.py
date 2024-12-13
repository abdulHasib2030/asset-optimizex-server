from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status, generics
from rest_framework.views import APIView
from account.serializers import *
from django.contrib.auth import authenticate
from account.renders import UserRenderer
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from account.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from account.utils import Util


# Create your views here.
### Generate Token Manually
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

########## User Account Register View ###############
class UserRegistrationView(APIView):
  renderer_classes = [UserRenderer]
  
  def post(self, request, format = None):
    serializer = UserRegistrationSerializer(data= request.data)   
    serializer.is_valid(raise_exception=True) #### raise exception use, not required if or else
    user = serializer.save()  
    token = get_tokens_for_user(user)
    return Response({'token':token, 'msg':'Registration Successful'}, status=status.HTTP_201_CREATED)


########### Login ################
class UserLoginView(APIView):
  renderer_classes = [UserRenderer]
  def post(self, request, format= None):
    serializer = UserLoginSerializer(data=request.data)
    serializer.is_valid(raise_exception= True)
    email = serializer.data.get('email')
    password = serializer.data.get('password')
    user = authenticate(email= email, password = password)
    
    if user is not None:
      token = get_tokens_for_user(user)
      return Response({'token': token, 'msg':"Login Success"}, status=status.HTTP_200_OK)
    else:
      return Response({'errors':{'non_field_errors': ['Email or Password is not Valid']}}, status=status.HTTP_404_NOT_FOUND)
             
########### User Profile ################
class UserProfileView(APIView):
  renderer_classes = [UserRenderer]
  permission_classes = [IsAuthenticated]
   
  def get(self, request, format = None):
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data, status = status.HTTP_200_OK)

########## User Update Profile ##########
class UserUpdateProfileView(generics.UpdateAPIView):
  queryset = User.objects.all()
  permission_classes = [IsAuthenticated]
  serializer_class = UserProfileUpdateSerializer
  
########## USer Change PAssword ######
class UserChangePasswordView(APIView):
  renderer_classes = [UserRenderer]
  permission_classes = [IsAuthenticated]
  def post(self, request, format= None):
    serializer = UserChangePasswordSerializer(data= request.data, context = {'user': request.user})
    serializer.is_valid(raise_exception=True)
    return Response({'msg': 'password change successfully'})
    
############ send email Password Reset
class SendPasswordResetEmailView(APIView):
  renderer_classes = [UserRenderer]
  def post(self, request, format = None):
    serializer = SendPasswordEmailSerializer(data= request.data)
    serializer.is_valid(raise_exception= True)
    return Response({'msg':'Password Reset Link send. Please Check Your Email'}, status = status.HTTP_200_OK)
    
######### UserPasswordResetView###
class UserPasswordResetView(APIView):
  renderer_classes = [UserRenderer]
  def post(self, request, uid, token,  format=None):
    serializer = UserPasswordResetSerializer(data=request.data, context = {'uid': uid, 'token': token})
    serializer.is_valid(raise_exception= True)
    return Response({'msg': 'password change successfully'}, status=status.HTTP_200_OK)
    



