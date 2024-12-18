from datetime import timezone
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
    image = models.ImageField(upload_to='media/posts/photos/', blank=False, null=False)
    
    def save(self, *args, **kwargs):
        self.post_type = 'photo'
        super().save(*args, **kwargs)


class VideoPost(Post):
    """Video post"""
    video = models.FileField(upload_to='media/posts/videos/', blank=False, null=False)
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
    
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='comments')
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'

    def __str__(self):
        return f"Comment by {self.user.user_name} on {self.post}"



