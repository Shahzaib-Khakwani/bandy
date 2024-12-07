from django.db import models
from account.models import CustomUser
from django.utils.timezone import now


class Post(models.Model):
    """Base Post model"""
    POST_TYPES = (
        ('text', 'Text Post'),
        ('photo', 'Photo Post'),
        ('video', 'Video Post'),
        ('link', 'Link Post'),
    )
    
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    post_type = models.CharField(max_length=10, choices=POST_TYPES)
    caption = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.post_type.capitalize()} post by {self.author.user_name}"


class TextPost(Post):
    """Text-only post"""
    content = models.TextField()
    
    def save(self, *args, **kwargs):
        self.post_type = 'text'
        super().save(*args, **kwargs)


class PhotoPost(Post):
    """Photo post"""
    image = models.ImageField(upload_to='posts/photos/', blank=False, null=False)
    
    def save(self, *args, **kwargs):
        self.post_type = 'photo'
        super().save(*args, **kwargs)


class VideoPost(Post):
    """Video post"""
    video = models.FileField(upload_to='posts/videos/', blank=False, null=False)
    duration = models.DurationField(blank=True, null=True)
    
    def save(self, *args, **kwargs):
        self.post_type = 'video'
        super().save(*args, **kwargs)


class LinkPost(Post):
    """Link post"""
    url = models.URLField()
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    
    def save(self, *args, **kwargs):
        self.post_type = 'link'
        super().save(*args, **kwargs)


class Like(models.Model):
    """Like model for posts"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'post']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.user_name} likes {self.post}"


class Comment(models.Model):
    """Comment model for posts"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comment by {self.author.user_name} on {self.post}"
    
    @property
    def is_reply(self):
        return self.parent is not None


class CommentLike(models.Model):
    """Like model for comments"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'comment']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.user_name} likes comment by {self.comment.author.user_name}"
