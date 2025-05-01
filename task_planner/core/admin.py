from django.contrib import admin, messages
from django.conf import settings
import requests

from .models import User, Team, Board, Task

# Custom export action
@admin.action(description='Export selected boards to file (via API)')
def export_boards(modeladmin, request, queryset):
    for board in queryset:
        try:
            response = requests.post(
                f"http://127.0.0.1:8000/api/board/export/",
                json={"id": str(board.id)}
            )
            if response.status_code == 200:
                filename = response.json().get("out_file", "export.txt")
                messages.success(request, f'Board "{board.name}" exported to {filename}.')
            else:
                messages.error(request, f'Failed to export board "{board.name}".')
        except Exception as e:
            messages.error(request, f'Error exporting board "{board.name}": {e}')

#user create
@admin.action(description='Create selected users via API')
def create_users_via_api(modeladmin, request, queryset):
    for user in queryset:
        try:
            response = requests.post(
                "http://127.0.0.1:8000/api/user/create/",
                json={
                    "name": user.name,
                    "display_name": user.display_name
                }
            )
            if response.status_code == 201:
                messages.success(request, f'User "{user.name}" created via API.')
            else:
                error = response.json().get('error', 'Unknown error')
                messages.error(request, f'Failed to create user "{user.name}": {error}')
        except Exception as e:
            messages.error(request, f'Error creating user "{user.name}": {e}')

#team create
@admin.action(description='Create selected teams via API')
def create_teams_via_api(modeladmin, request, queryset):
    for team in queryset:
        try:
            # Extract user IDs from the related users field
            user_ids = list(team.users.values_list('id', flat=True))

            payload = {
                "name": team.name,
                "admin": str(team.admin.id) if team.admin else None,
                "users": [str(uid) for uid in user_ids]
            }

            response = requests.post(
                "http://127.0.0.1:8000/api/team/create/",
                json=payload
            )

            if response.status_code == 201:
                messages.success(request, f'Team "{team.name}" created via API.')
            else:
                error = response.json().get('error', 'Unknown error')
                messages.error(request, f'Failed to create team "{team.name}": {error}')
        except Exception as e:
            messages.error(request, f'Error creating team "{team.name}": {e}')
#board 
@admin.action(description='Create selected boards via API')
def create_boards_via_api(modeladmin, request, queryset):
    for board in queryset:
        try:
            payload = {
                "name": board.name,
                "description": board.description,
                "team_id": str(board.team.id),
                "creation_time": board.creation_time.isoformat() if board.creation_time else None
            }

            response = requests.post(
                "http://127.0.0.1:8000/api/board/create/",
                json=payload
            )

            if response.status_code == 201:
                messages.success(request, f'Board "{board.name}" created via API.')
            else:
                error = response.json().get('error', 'Unknown error')
                messages.error(request, f'Failed to create board "{board.name}": {error}')
        except Exception as e:
            messages.error(request, f'Error creating board "{board.name}": {e}')

#user list
@admin.action(description='Fetch all users via API')
def list_users_via_api(modeladmin, request, queryset):
    try:
        response = requests.get("http://127.0.0.1:8000/api/user/list/")
        if response.status_code == 200:
            users = response.json()
            messages.info(request, f"Users: {users}")
        else:
            messages.error(request, f"Failed to fetch users: {response.json().get('error')}")
    except Exception as e:
        messages.error(request, f"Error: {e}")

# task create
@admin.action(description='Create selected tasks via API')
def create_tasks_via_api(modeladmin, request, queryset):
    for task in queryset:
        try:
            # Prepare the payload to send to the API
            payload = {
                "title": task.title,
                "description": task.description,
                "status": task.status,
                "board_id": str(task.board.id),  # Assuming each task is assigned to a board
                "user_id": str(task.user.id) if task.user else None,  # If a user is assigned to the task
                "creation_time": task.creation_time.isoformat() if task.creation_time else None,
                "end_time": task.end_time.isoformat() if task.end_time else None,
            }

            # Send the request to the API to create the task
            response = requests.post(
                "http://127.0.0.1:8000/task/add/",  # Use the /task/add/ URL to add a new task
                json=payload
            )

            # Check the response from the API
            if response.status_code == 201:
                messages.success(request, f'Task "{task.title}" created via API.')
            else:
                error = response.json().get('error', 'Unknown error')
                messages.error(request, f'Failed to create task "{task.title}": {error}')
        except Exception as e:
            messages.error(request, f'Error creating task "{task.title}": {e}')


admin.site.site_header = "Task Planner"
admin.site.site_title = "Task Planner Admin Portal"
admin.site.index_title = "Welcome to Task Planner Admin"

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'display_name')
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return ('name',)
        return ()

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'admin', 'creation_time')
    filter_horizontal = ('users',)


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'team', 'status', 'creation_time', 'end_time')
    actions = [export_boards]  # 🔥 Add the export action here

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'board', 'user', 'status', 'creation_time')
