from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import Post
from account.models import CustomUser, Friendship
from .models import TextPost, PhotoPost, VideoPost, LinkPost
from .serializers import TextPostSerializer, PhotoPostSerializer, VideoPostSerializer, LinkPostSerializer

class FeedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        friends_ids = Friendship.objects.filter((Q(user=user) | Q(friend=user)) & Q(is_active=True)).values_list('friend_id', flat=True)

        posts = Post.objects.filter(author__id__in=friends_ids).order_by('-created_at')

        from .serializers import PostSerializer
        serializer = PostSerializer(posts, many=True)

        return Response(serializer.data, status=200)

class CreateTextPostView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = TextPostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)  # Assuming `request.user` is the logged-in user
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreatePhotoPostView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = PhotoPostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)  # Assuming `request.user` is the logged-in user
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateVideoPostView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = VideoPostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)  # Assuming `request.user` is the logged-in user
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateLinkPostView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = LinkPostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)  # Assuming `request.user` is the logged-in user
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
