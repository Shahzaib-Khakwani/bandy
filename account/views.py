from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from .serializers import CustomUserSerializer
from django.core.cache import cache
import uuid
from .tasks import send_otp_email
from django.shortcuts import get_object_or_404
from .models import CustomUser
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

class UpdateBioView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        try:
            bio = request.data.get('bio')
            
            if not bio:
                return Response(
                    {'message': 'Bio is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            request.user.about = bio
            request.user.save()
            
            return Response(
                {'message': 'Bio updated successfully'}, 
                status=status.HTTP_200_OK
            )
        
        except Exception as e:
            return Response(
                {'message': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
from rest_framework.renderers import JSONRenderer


class UserRegisteration(APIView):
    
    permission_classes = [AllowAny]
    
    @staticmethod
    def generate_uuid_otp():
        """Generate a unique OTP using UUID."""
        otp = str(uuid.uuid4())  
        return otp

    def post(self, request, format='json'):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                tries = cache.get(f"{user.id}-tries",0)
                if tries > 10:
                    return Response("Too Many Otp Requests Try After 5 hours", status=status.HTTP_400_BAD_REQUEST)
                otp = self.generate_uuid_otp()[:6]
                cache.set(f"{user.id}-otp", otp, timeout=1000)
                cache.set(f"{user.id}-tries", tries+1, timeout=18000)
                send_otp_email.delay(user.email, otp)
                data = json.dumps({'id':user.id})
                return Response({"message": "OTP sent to your email"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "OTP sent to your email"}, status=status.HTTP_200_OK)

    

class OTPverfication(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        
        user = get_object_or_404(CustomUser, email=email)
        
        correct_otp = cache.get(f"{user.id}-otp", 0)
        
            
        if correct_otp == otp:
            user.is_varified = True 
            user.is_active = True
            user.save()
            
            cache.delete(f"{user.id}-otp")
            
            return Response({
                "message": "OTP verified successfully"
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "message": "Wrong or expired OTP"
            }, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetRequest(APIView):
    permission_classes = [AllowAny]

    def generate_uuid_otp(self):
        """Generate a unique OTP using UUID (with only 6 digits)."""
        otp = str(uuid.uuid4())[:6]
        return otp

    def post(self, request, format='json'):
        email = request.data.get('email')
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        check = email.split('@')[1]
        if check != 'ISBSTUDENT.COMSATS.EDU.PK':
            return Response({"error": "Email must be from ISBSTUDENT.COMSATS.EDU.PK"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({"error": "User with this email does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            cache.delete(f"{id}-reset-otp")
        except:
            pass
        otp = self.generate_uuid_otp() 

        cache.set(f"{user.id}-reset-otp", otp, timeout=1000)

        send_otp_email.delay(user.email, otp)

        return Response({"message": "OTP sent to your email"}, status=status.HTTP_200_OK)




class OTPVerificationAndPasswordReset(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        otp = request.data.get('otp')
        new_password = request.data.get('new_password')
        email = request.data.get('email')

        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        check = email.split('@')[1]
        if check != 'ISBSTUDENT.COMSATS.EDU.PK':
            return Response({"error": "Email must be from ISBSTUDENT.COMSATS.EDU.PK"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({"error": "User with this email does not exist"}, status=status.HTTP_400_BAD_REQUEST)



        if not otp or not new_password:
            return Response({"error": "OTP and new password are required"}, status=status.HTTP_400_BAD_REQUEST)

        correct_otp = cache.get(f"{user.id}-reset-otp")

        if correct_otp is None:
            return Response({"error": "OTP has expired or is invalid"}, status=status.HTTP_400_BAD_REQUEST)

        if correct_otp != otp:
            return Response({"error": "Incorrect OTP"}, status=status.HTTP_400_BAD_REQUEST)

       
        user.set_password(new_password)
        user.save()

        cache.delete(f"{id}-reset-otp")

        return Response({"message": "Password reset successful"}, status=status.HTTP_200_OK)




class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id', None)

        if user_id:
            try:
                user = CustomUser.objects.get(id=user_id)
            except CustomUser.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'User not found.'
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            user = request.user

        if not user:
            return Response({
                'success': False,
                'error': 'User not found.'
            }, status=status.HTTP_404_NOT_FOUND)

        try:
            serializer = CustomUserSerializer(user)
            return Response({
                'success': True,
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class UpdateProfilePictureView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            # Get the current user
            user = request.user

            # Check if an image is provided
            if 'profile_picture' not in request.FILES:
                return Response({
                    'success': False, 
                    'detail': 'No profile picture uploaded'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Get the uploaded image
            image = request.FILES['profile_picture']

            # Update the user's profile picture
            user.image = image
            user.save()

            # Serialize the updated user data
            serializer = CustomUserSerializer(user)

            return Response({
                'success': True,
                'detail': 'Profile picture updated successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'success': False,
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)