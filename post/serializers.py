from .models import Comment
from account.models import CustomUser
from rest_framework import serializers
from .models import  Like, Post, TextPost, PhotoPost, VideoPost, LinkPost

class BasePostSerializer(serializers.ModelSerializer):
    """Base serializer for all post types"""
    author = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    
    class Meta:
        model = Post
        fields = ['id', 'author', 'created_at', 'updated_at', 'post_type', 'caption']
        read_only_fields = ['created_at', 'updated_at']


class TextPostSerializer(BasePostSerializer):
    """Serializer for Text Posts"""
    content = serializers.CharField(required=True)

    class Meta(BasePostSerializer.Meta):
        model = TextPost
        fields = BasePostSerializer.Meta.fields + ['content']

    def create(self, validated_data):
        return TextPost.objects.create(**validated_data)


class PhotoPostSerializer(BasePostSerializer):
    """Serializer for Photo Posts"""
    image = serializers.ImageField(required=True)

    class Meta(BasePostSerializer.Meta):
        model = PhotoPost
        fields = BasePostSerializer.Meta.fields + ['image']

    def create(self, validated_data):
        return PhotoPost.objects.create(**validated_data)


class VideoPostSerializer(BasePostSerializer):
    """Serializer for Video Posts"""
    video = serializers.FileField(required=True)
    duration = serializers.DurationField(required=False, allow_null=True)

    class Meta(BasePostSerializer.Meta):
        model = VideoPost
        fields = BasePostSerializer.Meta.fields + ['video', 'duration']

    def create(self, validated_data):
        return VideoPost.objects.create(**validated_data)


class LinkPostSerializer(BasePostSerializer):
    """Serializer for Link Posts"""
    url = serializers.URLField(required=True)
    title = serializers.CharField(max_length=255, required=True)
    description = serializers.CharField(required=False, allow_null=True)

    class Meta(BasePostSerializer.Meta):
        model = LinkPost
        fields = BasePostSerializer.Meta.fields + ['url', 'title', 'description']

    def create(self, validated_data):
        return LinkPost.objects.create(**validated_data)



#---------------------------------------------------------------------------------------------------------------------#

class CustomUserMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'user_name','image']

class LikeSerializer(serializers.ModelSerializer):
    user = CustomUserMinimalSerializer(read_only=True)

    class Meta:
        model = Like
        fields = ['id', 'user', 'created_at']



class PostSerializer(serializers.ModelSerializer):
    author = CustomUserMinimalSerializer(read_only=True)
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    content = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    video_url = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'author', 'created_at', 'updated_at',
            'post_type', 'caption', 'content', 'image_url',
            'video_url', 'duration', 'url', 'title',
            'description', 'likes_count', 'comments_count', 'is_liked'
        ]

    def get_is_liked(self, obj):
        user = self.context.get('request').user
        return obj.likes.filter(user=user).exists()

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_comments_count(self, obj):
        return obj.comments.count()

    def get_content(self, obj):
        if hasattr(obj, 'textpost'):
            return obj.textpost.content
        return None

    def get_image_url(self, obj):
        if hasattr(obj, 'photopost'):
            return obj.photopost.image.url if obj.photopost.image else None
        return None

    def get_video_url(self, obj):
        if hasattr(obj, 'videopost'):
            return obj.videopost.video.url if obj.videopost.video else None
        return None

    def get_duration(self, obj):
        if hasattr(obj, 'videopost'):
            return obj.videopost.duration
        return None

    def get_url(self, obj):
        if hasattr(obj, 'linkpost'):
            return obj.linkpost.url
        return None

    def get_title(self, obj):
        if hasattr(obj, 'linkpost'):
            return obj.linkpost.title
        return None

    def get_description(self, obj):
        if hasattr(obj, 'linkpost'):
            return obj.linkpost.description
        return None

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Remove None values based on post type
        if instance.post_type == 'text':
            fields_to_remove = ['image_url', 'video_url', 'duration', 'url', 'title', 'description']
        elif instance.post_type == 'photo':
            fields_to_remove = ['content', 'video_url', 'duration', 'url', 'title', 'description']
        elif instance.post_type == 'video':
            fields_to_remove = ['content', 'image_url', 'url', 'title', 'description']
        elif instance.post_type == 'link':
            fields_to_remove = ['content', 'image_url', 'video_url', 'duration']
        
        for field in fields_to_remove:
            representation.pop(field, None)
            
        return representation
    

class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for Comment model
    """
    user = CustomUserMinimalSerializer(read_only=True)
    post = PostSerializer(read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'post', 'user', 'content', 'created']
        read_only_fields = ['id', 'created']




class CommentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer specifically for creating comments
    """
    class Meta:
        model = Comment
        fields = ['post', 'content']