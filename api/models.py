from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    daily_hour_limit = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=6.0,
        help_text="Daily working hours limit for capacity calculation",
    )

    def __str__(self):
        return self.username


class Note(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)


class Activity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=100)
    course = models.CharField(max_length=255)
    event_date = models.DateTimeField(null=True, blank=True)
    due_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(max_length=20, default="pending")

    def __str__(self):
        return self.title


class Subtask(models.Model):
    STATUS_PENDING = "pending"
    STATUS_COMPLETED = "completed"
    STATUS_POSTPONED = "postponed"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_POSTPONED, "Postponed"),
    ]

    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name="subtasks")
    name = models.CharField(max_length=255)
    target_date = models.DateField()
    estimated_hours = models.DecimalField(max_digits=4, decimal_places=1)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    note = models.TextField(blank=True, default="")
    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.name
