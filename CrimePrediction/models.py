from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator


class Location(models.Model):
    name = models.CharField(max_length=48)
    description = models.TextField(max_length=600)

    def no_of_ratings(self):
        ratings = Rating.objects.filter(location=self)
        return len(ratings)

    def avg_rating(self):
        summation = 0
        ratings = Rating.objects.filter(location=self)
        for rating in ratings:
            summation += rating.stars

        if len(ratings) > 0:
            return summation / len(ratings)
        else:
            return 0


class Rating(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stars = models.FloatField(validators=[MinValueValidator(1),MaxValueValidator(5)])

    class Meta:
        unique_together = (('user', 'location'),)
        index_together = (('user', 'location'),)