from django.db import models

# Create your models here.
class Files(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.id}: {self.name}"

class Attribute(models.Model):
    feature = models.CharField(max_length=20)
    bodypart = models.CharField(max_length=20)
    value = models.CharField(max_length=100)
    images = models.TextField()

    def __str__(self):
        return f"{self.bodypart}_{self.feature}_{self.value} : {self.images}"

class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)