from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User, Team, Board, Task
from .serializers import UserSerializer
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils import timezone

class CreateUserView(APIView):
    def post(self, request):
        try:
            data = json.loads(request.body)
            name = data.get("name")
            display_name = data.get("display_name")

            if not name or not display_name:
                return Response({"error": "Both name and display_name are required"}, status=400)

            if len(name) > 64 or len(display_name) > 64:
                return Response({"error": "Max length for name/display_name is 64 characters"}, status=400)

            if User.objects.filter(name=name).exists():
                return Response({"error": "User with this name already exists"}, status=400)

            user = User.objects.create(name=name, display_name=display_name)
            return Response({"id": str(user.id)}, status=201)
        except Exception as e:
            return Response({"error": str(e)}, status=500)


class ListUsersView(APIView):
    def get(self, request):
        users = User.objects.all()
        serialized = UserSerializer(users, many=True)
        return Response(serialized.data, status=200)


class DescribeUserView(APIView):
    def post(self, request):
        try:
            data = json.loads(request.body)
            user_id = data.get("id")
            user = User.objects.get(id=user_id)
            return Response({
                "name": user.name,
                "description": user.display_name,
                "creation_time": user.creation_time
            })
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)


class UpdateUserView(APIView):
    def put(self, request):
        try:
            data = json.loads(request.body)
            user_id = data.get("id")
            update_data = data.get("user", {})
            display_name = update_data.get("display_name")

            if display_name and len(display_name) > 128:
                return Response({"error": "Display name too long (max 128)"}, status=400)

            user = User.objects.get(id=user_id)

            # name cannot be updated
            if update_data.get("name") and update_data["name"] != user.name:
                return Response({"error": "User name cannot be updated"}, status=400)

            user.display_name = display_name or user.display_name
            user.save()
            return Response({"message": "User updated"}, status=200)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)


class GetUserTeamsView(APIView):
    def post(self, request):
        try:
            data = json.loads(request.body)
            user_id = data.get("id")
            user = User.objects.get(id=user_id)
            teams = user.teams.all()

            result = [{
                "name": t.name,
                "description": t.description,
                "creation_time": t.creation_time
            } for t in teams]

            return Response(result, status=200)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

class CreateTeamView(APIView):
    def post(self, request):
        try:
            data = json.loads(request.body)
            name = data.get("name")
            description = data.get("description")
            admin_id = data.get("admin")

            if not all([name, description, admin_id]):
                return Response({"error": "Missing fields"}, status=400)

            if Team.objects.filter(name=name).exists():
                return Response({"error": "Team with this name already exists"}, status=400)

            if len(name) > 64 or len(description) > 128:
                return Response({"error": "Invalid field length"}, status=400)

            admin = User.objects.get(id=admin_id)
            team = Team.objects.create(name=name, description=description, admin=admin)
            team.users.add(admin)  # Add admin to team by default

            return Response({"id": str(team.id)}, status=201)
        except User.DoesNotExist:
            return Response({"error": "Admin user not found"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

class ListTeamsView(APIView):
    def get(self, request):
        teams = Team.objects.all()
        result = [{
            "name": team.name,
            "description": team.description,
            "creation_time": team.creation_time,
            "admin": str(team.admin.id)
        } for team in teams]
        return Response(result, status=200)

class DescribeTeamView(APIView):
    def post(self, request):
        try:
            data = json.loads(request.body)
            team_id = data.get("id")
            team = Team.objects.get(id=team_id)

            return Response({
                "name": team.name,
                "description": team.description,
                "creation_time": team.creation_time,
                "admin": str(team.admin.id)
            }, status=200)
        except Team.DoesNotExist:
            return Response({"error": "Team not found"}, status=404)

class UpdateTeamView(APIView):
    def put(self, request):
        try:
            data = json.loads(request.body)
            team_id = data.get("id")
            update_data = data.get("team")

            name = update_data.get("name")
            description = update_data.get("description")
            admin_id = update_data.get("admin")

            if len(name) > 64 or len(description) > 128:
                return Response({"error": "Field too long"}, status=400)

            team = Team.objects.get(id=team_id)

            if name != team.name and Team.objects.filter(name=name).exists():
                return Response({"error": "Team name must be unique"}, status=400)

            team.name = name
            team.description = description
            team.admin = User.objects.get(id=admin_id)
            team.save()

            return Response({"message": "Team updated"}, status=200)
        except Team.DoesNotExist:
            return Response({"error": "Team not found"}, status=404)
        except User.DoesNotExist:
            return Response({"error": "Admin user not found"}, status=404)
class AddUsersToTeamView(APIView):
    def post(self, request):
        try:
            data = json.loads(request.body)
            team_id = data.get("id")
            user_ids = data.get("users", [])

            if not team_id or not user_ids:
                return Response({"error": "Team ID and users list are required"}, status=400)

            if len(user_ids) > 50:
                return Response({"error": "Cannot add more than 50 users at once"}, status=400)

            team = Team.objects.get(id=team_id)
            users_to_add = User.objects.filter(id__in=user_ids)

            if users_to_add.count() != len(user_ids):
                return Response({"error": "One or more user IDs are invalid"}, status=400)

            team.users.add(*users_to_add)
            return Response({"message": "Users added"}, status=200)
        except Team.DoesNotExist:
            return Response({"error": "Team not found"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
class RemoveUsersFromTeamView(APIView):
    def post(self, request):
        try:
            data = json.loads(request.body)
            team_id = data.get("id")
            user_ids = data.get("users", [])

            if not team_id or not user_ids:
                return Response({"error": "Team ID and users list are required"}, status=400)

            if len(user_ids) > 50:
                return Response({"error": "Cannot remove more than 50 users at once"}, status=400)

            team = Team.objects.get(id=team_id)
            users_to_remove = User.objects.filter(id__in=user_ids)

            team.users.remove(*users_to_remove)
            return Response({"message": "Users removed"}, status=200)
        except Team.DoesNotExist:
            return Response({"error": "Team not found"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
        
        #   CHANGES MADE BY ZAID
class CreateBoardView(APIView):
    def post(self, request):
        try:
            data = request.data
            name = data.get("name")
            description = data.get("description")
            team_id = data.get("team_id")

            if not all([name, description, team_id]):
                return Response({"error": "Missing fields"}, status=400)

            if len(name) > 64 or len(description) > 128:
                return Response({"error": "Invalid field length"}, status=400)

            team = Team.objects.get(id=team_id)

            if Board.objects.filter(team=team, name=name).exists():
                return Response({"error": "Board name must be unique per team"}, status=400)

            board = Board.objects.create(name=name, description=description, team=team)
            return Response({"id": str(board.id)}, status=201)

        except Team.DoesNotExist:
            return Response({"error": "Team not found"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
class CloseBoardView(APIView):
    def post(self, request):
        try:
            board_id = request.data.get("id")
            board = Board.objects.get(id=board_id)

            if board.tasks.exclude(status='COMPLETE').exists():
                return Response({"error": "Cannot close board until all tasks are COMPLETE"}, status=400)

            board.status = 'CLOSED'
            board.end_time = timezone.now()
            board.save()

            return Response({"message": "Board closed successfully"}, status=200)

        except Board.DoesNotExist:
            return Response({"error": "Board not found"}, status=404)
        
class AddTaskView(APIView):
    def post(self, request):
        try:
            data = request.data
            title = data.get("title")
            description = data.get("description")
            board_id = data.get("board_id")
            user_id = data.get("user_id")

            if not all([title, description, board_id, user_id]):
                return Response({"error": "Missing fields"}, status=400)

            if len(title) > 64 or len(description) > 128:
                return Response({"error": "Invalid field length"}, status=400)

            board = Board.objects.get(id=board_id)
            if board.status != "OPEN":
                return Response({"error": "Cannot add task to a closed board"}, status=400)

            if Task.objects.filter(board=board, title=title).exists():
                return Response({"error": "Task title must be unique for this board"}, status=400)

            user = User.objects.get(id=user_id)

            task = Task.objects.create(
                title=title, description=description, board=board, user=user
            )
            return Response({"id": str(task.id)}, status=201)

        except Board.DoesNotExist:
            return Response({"error": "Board not found"}, status=404)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

class UpdateTaskStatusView(APIView):
    def put(self, request):
        try:
            task_id = request.data.get("id")
            new_status = request.data.get("status")

            if new_status not in ["OPEN", "IN_PROGRESS", "COMPLETE"]:
                return Response({"error": "Invalid status"}, status=400)

            task = Task.objects.get(id=task_id)
            task.status = new_status
            task.save()

            return Response({"message": "Task status updated"}, status=200)

        except Task.DoesNotExist:
            return Response({"error": "Task not found"}, status=404)

class ListBoardsView(APIView):
    def post(self, request):
        try:
            team_id = request.data.get("id")
            team = Team.objects.get(id=team_id)

            boards = team.boards.filter(status='OPEN')

            result = [{"id": str(board.id), "name": board.name} for board in boards]
            return Response(result, status=200)

        except Team.DoesNotExist:
            return Response({"error": "Team not found"}, status=404)

import os

class ExportBoardView(APIView):
    def post(self, request):
        try:
            board_id = request.data.get("id")
            board = Board.objects.get(id=board_id)

            filename = f"{board.name.replace(' ', '_')}_{board.id}.txt"
            output_dir = "out"
            os.makedirs(output_dir, exist_ok=True)
            file_path = os.path.join(output_dir, filename)

            with open(file_path, 'w') as f:
                f.write(f"Board: {board.name}\n")
                f.write(f"Description: {board.description}\n")
                f.write(f"Status: {board.status}\n")
                f.write(f"Created: {board.creation_time}\n")
                f.write(f"Ended: {board.end_time}\n\n")

                f.write("Tasks:\n")
                for task in board.tasks.all():
                    f.write(f"- [{task.status}] {task.title} (Assigned to: {task.user.name})\n")

            return Response({"out_file": file_path}, status=200)

        except Board.DoesNotExist:
            return Response({"error": "Board not found"}, status=404)

