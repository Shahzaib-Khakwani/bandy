from rest_framework import serializers
from .models import Post, TextPost, PhotoPost, VideoPost, LinkPost
from account.models import CustomUser

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'user_name', 'first_name', 'last_name']

class PostSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()

    class Meta:
        model = Post
        fields = ['id', 'author', 'created_at', 'post_type', 'caption']

class TextPostSerializer(PostSerializer):
    content = serializers.CharField()

    class Meta(PostSerializer.Meta):
        model = TextPost
        fields = PostSerializer.Meta.fields + ['content']

class PhotoPostSerializer(PostSerializer):
    image = serializers.ImageField()

    class Meta(PostSerializer.Meta):
        model = PhotoPost
        fields = PostSerializer.Meta.fields + ['image']

class VideoPostSerializer(PostSerializer):
    video = serializers.FileField()
    duration = serializers.DurationField()

    class Meta(PostSerializer.Meta):
        model = VideoPost
        fields = PostSerializer.Meta.fields + ['video', 'duration']

class LinkPostSerializer(PostSerializer):
    url = serializers.URLField()
    title = serializers.CharField()
    description = serializers.CharField()

    class Meta(PostSerializer.Meta):
        model = LinkPost
        fields = PostSerializer.Meta.fields + ['url', 'title', 'description']
