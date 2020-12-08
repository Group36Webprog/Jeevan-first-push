from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    favourite_category = models.CharField(max_length=999,blank=True, null=True)
    picture = models.ImageField(upload_to='picture', blank=True, null=True)
    date_of_birth = models.DateField()

class Article(models.Model):
	article_name = models.CharField(max_length=999)
	article_category = models.CharField(max_length=999)
	article_description = models.CharField(max_length=999)
	article_likes = models.ManyToManyField(User, related_name='article_likes')
	article_created_time = models.DateTimeField(default=datetime.now)

class Comment(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="article")
	comment_text = models.CharField(max_length=999)
	comment_created_time = models.DateTimeField(default=datetime.now)