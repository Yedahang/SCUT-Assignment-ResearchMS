import app.views

from django.urls import path

urlpatterns = [
    path('<str:module>/', app.views.SysView.as_view()),
    path('researchRooms/<str:module>/', app.views.ResearchRoomsView.as_view()),#研究室
    path('projects/<str:module>/', app.views.ProjectsView.as_view()),#项目
    path('projects_participators/<str:module>/', app.views.ProjectResearcherView.as_view()),#项目参与人员
    path('offices/<str:module>/', app.views.OfficesView.as_view()),#办公场地
    path('subprojects/<str:module>/', app.views.SubprojectsView.as_view()),#子课题
    path('organizations/<str:module>/', app.views.OrganizationsView.as_view()),#单位信息
    path('contacts/<str:module>/', app.views.ContactsView.as_view()),
    path('organization_contacts/<str:module>/', app.views.Organization_contactsView.as_view()),#单位联系人信息
    path('secretaries/<str:module>/', app.views.SecretariesView.as_view()),#秘书
    path('users/<str:module>/', app.views.UsersView.as_view()),
    path('researchers/<str:module>/', app.views.ResearchersView.as_view()), #科研人员
    path('directors/<str:module>/', app.views.DirectorsView.as_view()),#主任
    path('projectLogs/<str:module>/', app.views.ProjectLogsView.as_view()),
    path('achievements/<str:module>/', app.views.AchievementsView.as_view()),
    path('achievements_papers/<str:module>/', app.views.AchievementsPapersView.as_view()),
    path('achievements_patents/<str:module>/', app.views.AchievementsPatentsPapersView.as_view()),
    path('achievements_softwareCopyrights/<str:module>/', app.views.AchievementsSoftwareCopyrightsPapersView.as_view()),
]