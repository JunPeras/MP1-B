from django.db import models
from django.contrib.auth.models import User



class Note(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

class Activity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=100)
    course = models.CharField(max_length=255)
    event_date = models.DateField(null=True, blank=True)
    due_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=20,
        default="pending"
    )

    def __str__(self):
        return self.title


class Subtask(models.Model):
    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name="subtasks"
    )
    name = models.CharField(max_length=255)
    target_date = models.DateField()
    estimated_hours = models.DecimalField(max_digits=4, decimal_places=1)
    created_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name
    


