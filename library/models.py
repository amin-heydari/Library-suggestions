from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Books(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    genre = models.CharField(max_length=50)

    class Meta:
        unique_together = ('title', 'author', 'genre')

    def __str__(self):
        return self.title


class Reviews(models.Model):
    book = models.ForeignKey(Books, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()

    class Meta:
        unique_together = ('book', 'user')
        constraints = [
            models.CheckConstraint(check=models.Q(rating__gte=1, rating__lte=5), name='rating_range')
        ]

    def __str__(self):
        return f'{self.book.title} - {self.user.username} - {self.rating}'
