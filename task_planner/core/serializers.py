from rest_framework import serializers
from .models import User, Team, Board, Task


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'display_name', 'creation_time']


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['id', 'name', 'description', 'creation_time', 'admin']


class TeamListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['name', 'description', 'creation_time', 'admin']


class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = ['id', 'name', 'description', 'team', 'creation_time', 'end_time', 'status']


class BoardListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = ['id', 'name']


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'board', 'user', 'creation_time', 'status']
