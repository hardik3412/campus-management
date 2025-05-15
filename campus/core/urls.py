from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register/', views.register_student, name='register_student'),
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('course/<int:course_id>/attendance/', views.take_attendance, name='take_attendance'),
    path('attendance/success/', views.attendance_success, name='attendance_success'),
    path('assignments/', views.assignment_list, name='assignment_list'),
    path('assignments/add/', views.add_assignment, name='add_assignment'),
    path('assignments/<int:assignment_id>/submit/', views.submit_assignment, name='submit_assignment'),
    path('assignments/<int:assignment_id>/submissions/', views.assignment_submissions, name='assignment_submissions'),
    path('submissions/<int:submission_id>/grade/', views.grade_submission, name='grade_submission'),
    path('notifications/mark-read/', views.mark_notifications_read, name='mark_notifications_read'),
    path('attendance/mark/<int:course_id>/', views.mark_attendance, name='mark_attendance'),
    path('attendance/student/', views.student_attendance, name='student_attendance'),
    path('teacher-dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('attendance/', views.attendance_page, name='attendance_page'),
    path('assignments/<int:pk>/', views.assignment_detail, name='assignment_detail'),





]