from django.db import models
import uuid
from django.core.exceptions import ValidationError


class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=64, unique=True)
    display_name = models.CharField(max_length=64)
    creation_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Team(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=64, unique=True)
    description = models.CharField(max_length=128)
    creation_time = models.DateTimeField(auto_now_add=True)
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_teams')
    users = models.ManyToManyField(User, related_name='teams', blank=True)

    def __str__(self):
        return self.name

    def clean(self):
        # Check if the number of users exceeds 50
        if self.users.count() > 50:
            raise ValidationError("A team cannot have more than 50 members.")
        
class Board(models.Model):
    STATUS_CHOICES = (
        ('OPEN', 'Open'),
        ('CLOSED', 'Closed'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=128)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='boards')
    creation_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='OPEN')

    class Meta:
        unique_together = ('team', 'name')  # board name must be unique for a team

    def __str__(self):
        return self.name


class Task(models.Model):
    STATUS_CHOICES = (
        ('OPEN', 'Open'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETE', 'Complete'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=128)
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='tasks')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    creation_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')

    class Meta:
        unique_together = ('board', 'title')  # task title must be unique per board

    def __str__(self):
        return self.title
