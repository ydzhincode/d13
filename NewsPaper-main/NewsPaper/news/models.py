from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum
from django.contrib.auth.forms import UserCreationForm
from django import forms


class Author(models.Model):
    authorUser = models.OneToOneField(User, on_delete=models.CASCADE)
    ratingAuthor = models.SmallIntegerField(default=0)

    def __str__(self):
        return self.authorUser.username

    def update_rating(self):
        postRat = self.post_set.all().aggregate(postRating=Sum('rating'))
        pRat = 0
        pRat += postRat.get('postRating')

        commentRat = self.authorUser.comment_set.all().aggregate(commentRating=Sum('rating'))
        cRat = 0
        cRat += commentRat.get('commentRating')

        posts = self.post_set.all()
        comPostRat = 0
        for post in posts:
            comPostRow = post.comment_set.all().aggregate(cpRating=Sum('rating'))
            comPostRat += comPostRow.get('cpRating')

        self.ratingAuthor = pRat * 3 + cRat + comPostRat
        self.save()


class Category(models.Model):
    name = models.CharField(max_length=64, unique=True)
    subscribers = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/news/categories/{self.id}'


class Post(models.Model):
    news = 'NW'
    article = 'AR'

    TYPES = [
        (news, 'Новость'),
        (article, 'Статья'),
    ]

    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    categoryType = models.CharField(max_length=2, choices=TYPES, default=news)
    dateCreation = models.DateTimeField(auto_now_add=True)
    postCategory = models.ManyToManyField(Category, through='PostCategory')
    title = models.CharField(max_length=128)
    text = models.TextField()
    rating = models.SmallIntegerField(default=0)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return f'/news/{self.id}'

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        return self.text[0:123] + '...'


class PostCategory(models.Model):
    postThrough = models.ForeignKey(Post, on_delete=models.CASCADE)
    categoryThrough = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.postThrough.title} ===> {self.categoryThrough.name}'


class Comment(models.Model):
    commentPost = models.ForeignKey(Post, on_delete=models.CASCADE)
    commentUser = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    dateCreation = models.DateTimeField(auto_now_add=True)
    rating = models.SmallIntegerField(default=0)

    def __str__(self):
        return f'{self.dateCreation} {self.commentUser.username} {self.commentPost.title}'

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()


class BaseRegisterForm(UserCreationForm):
    email = forms.EmailField(label="Email")
    first_name = forms.CharField(label="Имя")  # опционально
    last_name = forms.CharField(label="Фамилия")  # опционально

    class Meta:
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2',
        )
