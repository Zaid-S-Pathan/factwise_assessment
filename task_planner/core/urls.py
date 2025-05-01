from django.urls import path
from .views import (
    CreateUserView, ListUsersView, DescribeUserView, UpdateUserView, GetUserTeamsView,
    CreateTeamView, ListTeamsView, DescribeTeamView, UpdateTeamView,
    AddUsersToTeamView, RemoveUsersFromTeamView,
    CreateBoardView, CloseBoardView, ListBoardsView, ExportBoardView,
    AddTaskView, UpdateTaskStatusView,


)

urlpatterns = [
    path("user/create/", CreateUserView.as_view(), name="create_user"),
    path("user/list/", ListUsersView.as_view(), name="list_users"),
    path("user/describe/", DescribeUserView.as_view(), name="describe_user"),
    path("user/update/", UpdateUserView.as_view(), name="update_user"),
    path("user/teams/", GetUserTeamsView.as_view(), name="get_user_teams"),

    
    path('team/create/', CreateTeamView.as_view()),
    path('team/list/', ListTeamsView.as_view()),
    path('team/describe/', DescribeTeamView.as_view()),
    path('team/update/', UpdateTeamView.as_view()),

    path('team/add-users/', AddUsersToTeamView.as_view(), name='add-users-to-team'),
    path('team/remove-users/', RemoveUsersFromTeamView.as_view(), name='remove-users-from-team'),

    path('board/create/', CreateBoardView.as_view()),
    path('board/close/', CloseBoardView.as_view()),
    path('board/list/', ListBoardsView.as_view()),
    path('board/export/', ExportBoardView.as_view()),

    path('task/add/', AddTaskView.as_view()),
    path('task/update-status/', UpdateTaskStatusView.as_view()),
]
