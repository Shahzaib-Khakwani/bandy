from django.urls import path
from .views import UpdateBioView, UpdateProfilePictureView, UserRegisteration, OTPverfication, PasswordResetRequest, OTPVerificationAndPasswordReset
from .views import UserDetailView


urlpatterns = [
    path('register/', UserRegisteration.as_view(), name='user-registration'),
    
    path('verify-otp/', OTPverfication.as_view(), name='otp-verification'),
    
    path('password-reset-verification/', OTPVerificationAndPasswordReset.as_view(), name='password-reset-request'),
    
    path('password-reset-request/', PasswordResetRequest.as_view(), name='password-reset'),

    path('user/<int:user_id>/', UserDetailView.as_view(), name='user-detail'),
    path('user/', UserDetailView.as_view(), name='user-detail-self'), 

    path('upload-profile-picture/', UpdateProfilePictureView.as_view(), name='upload_profile_picture'), 

    path('update-bio/', UpdateBioView.as_view(), name='update_bio'),
]
