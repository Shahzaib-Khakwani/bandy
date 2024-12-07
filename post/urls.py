from django.urls import path
from .views import FeedView, CreateTextPostView, CreatePhotoPostView, CreateVideoPostView, CreateLinkPostView

urlpatterns = [
    path('feed/', FeedView.as_view(), name='user-feed'),
    path('create/text/', CreateTextPostView.as_view(), name='create_text_post'),
    path('create/photo/', CreatePhotoPostView.as_view(), name='create_photo_post'),
    path('create/video/', CreateVideoPostView.as_view(), name='create_video_post'),
    path('create/link/', CreateLinkPostView.as_view(), name='create_link_post'),

]
