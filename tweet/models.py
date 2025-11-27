from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Tweet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(max_length=500)
    photo = models.ImageField(upload_to='photos/', blank=True, null=True)
    created_at = models.DateField(auto_now=True)

    def __str__(self):
        return f'{self.user.username}-{self.text[:10]}'

    def total_likes(self):
        return self.likes.count()


class Like(models.Model):
    tweet = models.ForeignKey(Tweet, related_name="likes", on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    session_id = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        unique_together = ('tweet', 'session_id')


class Comment(models.Model):
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_id = models.CharField(max_length=100, null=True, blank=True)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_photo = models.ImageField(
        upload_to='profile_pics/',
        default='photos/man1.webp',
        blank=True, null=True
    )

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()
