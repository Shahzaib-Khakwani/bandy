from django.shortcuts import get_object_or_404
import json
from tokenize import Comment
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, generics

from django.db.models import Q
from .models import Like, Post
from account.models import CustomUser, Friendship
from .models import TextPost, PhotoPost, VideoPost, LinkPost, Comment   
from .serializers import TextPostSerializer, PhotoPostSerializer, VideoPostSerializer, LinkPostSerializer, PostSerializer
from .serializers import CommentCreateSerializer, CommentSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import APIException
from django.core.exceptions import ValidationError



class CustomCommentPagination(PageNumberPagination):
    """
    Custom pagination for comments
    Default page size is 10 comments per page
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class CustomPagination(PageNumberPagination):
    page_size = 4
    page_size_query_param = 'page_size'
    max_page_size = 100

class FeedView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    def get(self, request, *args, **kwargs):
        try:
            user = request.user
            
            
            # friends_ids = Friendship.objects.filter(
            #     (Q(user=user) | Q(friend=user)) & Q(is_active=True)
            # ).values_list('friend_id', flat=True)
            friends_ids = set(
                list(Friendship.objects.filter(user=user, is_active=True).values_list('friend_id', flat=True)) +
                list(Friendship.objects.filter(friend=user, is_active=True).values_list('user_id', flat=True))
                )
            friends_ids.add(user.id)
            print(friends_ids)
            posts = Post.objects.filter(
                author__id__in=friends_ids
            ).order_by('-created_at')
            # posts = Post.objects.filter(
            #     author=user
            # ).order_by('-created_at')
            paginator = self.pagination_class()
            paginated_posts = paginator.paginate_queryset(posts, request)
            serializer = PostSerializer(paginated_posts, many=True, context={'request': request})
            # print(paginator.get_paginated_response(serializer.data))
            return paginator.get_paginated_response(serializer.data)
        except ValidationError as e:
            print(e)
            return Response({'error': 'Validation error','detail': str(e)}, status=400)
        except Post.DoesNotExist:
            print(e)
            return Response({'error': 'No posts found'}, status=404)
        except Friendship.DoesNotExist:
            print(e)
            return Response({'error': 'No friendships found'}, status=404)
        except Exception as e:
            print(e)
            return Response({'error': 'An unexpected error occurred','detail': str(e)}, status=500)

class CreatePostView(APIView):
    """Generic view for creating different types of posts"""
    permission_classes = [IsAuthenticated]

    def get_serializer(self, post_type):
        """Select appropriate serializer based on post type"""
        serializers_map = {
            'text': TextPostSerializer,
            'photo': PhotoPostSerializer,
            'video': VideoPostSerializer,
            'link': LinkPostSerializer
        }
        return serializers_map.get(post_type)

    def post(self, request, *args, **kwargs):
        post_type = request.data.get('post_type')
        
        if not post_type or post_type not in ['text', 'photo', 'video', 'link']:
            return Response(
                {'error': 'Invalid or missing post type'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer_class = self.get_serializer(post_type)
        
        serializer = serializer_class(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            post = serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AddLikeView(APIView):
    def post(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
            like, created = Like.objects.get_or_create(user=request.user, post=post)
            if not created:
                like.delete()
                message = 'Like removed'
            else:
                message = 'Like added'
            # Always include the updated post
            post_data = PostSerializer(post, context={'request': request}).data
            return Response(
                status=status.HTTP_200_OK,
                data={'message': message, 'post': post_data}
            )
        except Post.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND, data={'error': 'Post not found'})





class CustomCommentPagination(PageNumberPagination):
    """
    Custom pagination for comments
    Returns paginated results with 'results', 'count', and 'next'
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50

    def get_paginated_response(self, data):
        print(data)
        return Response({
            'success': True,
            'message': 'Comments fetched successfully.',
            'data': {
                'results': data,
                'count': self.page.paginator.count,
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
            }
        })


class CommentListCreateView(generics.ListCreateAPIView):
    """
    View to list and create comments for a specific post
    """
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomCommentPagination

    def get_queryset(self):
        """
        Fetches comments for the given post ID.
        """
        post_id = self.kwargs.get('post_id')
        if not post_id:
            raise ValidationError({"error": "Post ID is required."})
        return Comment.objects.filter(post_id=post_id)

    def create(self, request, *args, **kwargs):
        """
        Creates a new comment or reply for the specified post.
        Returns a standardized response object.
        """
        post_id = self.kwargs.get('post_id')
        if not post_id:
            return Response(
                {"success": False, "message": "Post ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if isinstance(request.data, str):
            try:
                request_data = json.loads(request.data)
            except json.JSONDecodeError:
                return Response({"error": "Invalid JSON"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            request_data = request.data

        create_data = {
            'post': post_id,
            'content': request_data.get('content'),
        
        }

        # Validate and save the comment
        serializer = CommentCreateSerializer(data=create_data)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user)
        except ValidationError as e:
            return Response(
                {"success": False, "message": "Validation failed.", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Retrieve the newly created comment for the response
        comment = Comment.objects.get(id=serializer.instance.id)
        response_serializer = CommentSerializer(comment, context={'request': request})

        return Response(
            {
                "success": True,
                "message": "Comment created successfully.",
                "comment": response_serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )


#----------------------------------------------------------------------------------------------#
###Post by users
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000

class UserPostsView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get(self, request, *args, **kwargs):
        try:
            user = request.user
            posts = Post.objects.filter(author=user)
            paginator = self.pagination_class()
            result_page = paginator.paginate_queryset(posts, request)
            serializer = PostSerializer(result_page, many=True, context={'request': request})
            
            paginated_response = paginator.get_paginated_response(serializer.data)
            data = paginated_response.data
            
            return Response({
                'success': True,
                'data': data,
            }, status=status.HTTP_200_OK)
        
        except Post.DoesNotExist:
            return Response({
                'success': False,
                'error': 'No posts found.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            print(e)
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)








class PostDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, post_id):
        try:
            post = Post.objects.get_subclass(id=post_id)
            
            if request.user != post.author:
                return Response(
                    {"detail": "You do not have permission to delete this post."}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            post.delete()
            
            return Response(
                {"detail": "Post deleted successfully."}, 
                status=status.HTTP_204_NO_CONTENT
            )
        
        except Post.DoesNotExist:
            return Response(
                {"detail": "Post not found."}, 
                status=status.HTTP_404_NOT_FOUND
            )
