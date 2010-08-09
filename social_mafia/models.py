from django.db import models

class User(models.Model):
    name = models.CharField(max_length=40)

    def __unicode__(self):
        return self.name


class Story(models.Model):
    slug = models.CharField(max_length=200)

    def __unicode__(self):
        return self.slug


class Vote(models.Model):
    user = models.ForeignKey(User)
    story = models.ForeignKey(Story)
    value = models.IntegerField()
