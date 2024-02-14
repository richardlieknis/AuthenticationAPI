from urllib.parse import quote
from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import status
from rest_framework.generics import UpdateAPIView
from rest_framework.views import APIView
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from .models import User
import jwt
import datetime

from .serializers import UserSerializer

# Create your views here.


class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class LoginView(APIView):
    def post(self, request):
        email = request.data['email']
        password = request.data['password']
        user = User.objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed('User not found!')

        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password!')

        payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, 'secret',
                           algorithm='HS256')

        response = Response()
        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            'jwt': token,
            'message': 'You logged in successfully!'
        }

        return response


class UserView(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')

        user = User.objects.filter(id=payload['id']).first()
        serializer = UserSerializer(user)
        return Response(serializer.data)


class LogoutView(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message': 'You logged out successfully!'
        }
        return response


class ResetPassword(APIView):
    def post(self, request):
        email = request.data.get('email', None)

        if not email:
            raise AuthenticationFailed('Email is required for password reset.')

        user = User.objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed('User with this email does not exist.')

        # Generate a token for password reset
        reset_token = jwt.encode(
            {'user_id': user.id}, 'reset-secret', algorithm='HS256')

        # Replace the dots in the token with dashes
        # So that the token can be passed in the URL
        tokenWithoutDots = reset_token.replace(".", ",")

        # Send an email with the reset link containing the token
        # Replace with your frontend URL
        reset_link = f"{settings.FRONTEND_URL}/reset-password/{tokenWithoutDots}"
        send_mail(
            'Password Reset',
            f'Click on the following link to reset your password: {reset_link}',
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )

        return Response({'message': 'Password reset link sent to your email.'}, status=status.HTTP_200_OK)


class CompleteResetPassword(UpdateAPIView):
    def patch(self, request, token):
        try:
            payload = jwt.decode(token, 'reset-secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Password reset link has expired.')

        user = User.objects.filter(id=payload['user_id']).first()

        if user is None:
            raise AuthenticationFailed('User not found.')

        new_password = request.data.get('password', None)

        if not new_password:
            raise AuthenticationFailed('New password is required.')

        # Set the new password and save the user
        user.set_password(new_password)
        user.save()

        return Response({'message': 'Password reset successful.'}, status=status.HTTP_200_OK)
