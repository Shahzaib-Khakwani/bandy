from django.urls import path
from .views import UserRegisteration, OTPverfication, PasswordResetRequest, OTPVerificationAndPasswordReset



urlpatterns = [
    path('register/', UserRegisteration.as_view(), name='user-registration'),
    
    path('verify-otp/<int:id>/', OTPverfication.as_view(), name='otp-verification'),
    
    path('password-reset_verification/', OTPVerificationAndPasswordReset.as_view(), name='password-reset-request'),
    
    path('password-reset-request/', PasswordResetRequest.as_view(), name='password-reset'),
]
