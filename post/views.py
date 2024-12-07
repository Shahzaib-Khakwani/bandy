from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Post
from account.models import CustomUser

class FeedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        friends_ids = user.friends.filter(friendship__is_active=True).values_list('id', flat=True)

        posts = Post.objects.filter(author__id__in=friends_ids).order_by('-created_at')

        from .serializers import PostSerializer
        serializer = PostSerializer(posts, many=True)

        return Response(serializer.data, status=200)
