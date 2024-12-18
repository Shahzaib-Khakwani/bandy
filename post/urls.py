from django.urls import path
from .views import AddLikeView, FeedView,CreatePostView, UserPostsView
from .views import CommentListCreateView
urlpatterns = [
    path('feed/', FeedView.as_view(), name='user-feed'),
    path('create/post/', CreatePostView.as_view(), name='create_post'),
    
    path('like/post/<int:post_id>/', AddLikeView.as_view(), name='like_post'),
    path('<int:post_id>/comments/', CommentListCreateView.as_view(), name='post-comments'),

    path('user/posts/', UserPostsView.as_view(), name='user-posts'),

    path('delete/<int:post_id>/', PostDeleteView.as_view(), name='delete_post'),

]
