from datetime import date
from pyexpat.errors import messages
from django.shortcuts import render, redirect
from .forms import UserForm, StudentForm,AssignmentForm,AssignmentSubmissionForm,AttendanceForm
from django.contrib.auth import login
from .models import Attendance, Student, Course,Assignment,AssignmentSubmission,Notification
from django.utils import timezone           
from django.forms import modelformset_factory
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from .forms import GradeSubmissionForm
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.http import JsonResponse

def register_student(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        student_form = StudentForm(request.POST)

        if user_form.is_valid() and student_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user.password)  # Hash the password
            user.save()

            student = student_form.save(commit=False)
            student.user = user
            student.save()

            login(request, user)  # Log the user in
            return redirect('student_dashboard')  # Redirect to a placeholder view

    else:
        user_form = UserForm()
        student_form = StudentForm()

    return render(request, 'core/register.html', {
        'user_form': user_form,
        'student_form': student_form
    })


@login_required
def student_dashboard(request):
    # return render(request, 'core/dashboard.html')
    if request.user.is_staff:
        assignments = Assignment.objects.all()
    else:
        assignments = Assignment.objects.all()  # Or filter by student class if implemented

    return render(request, 'core/dashboard.html', {
        'assignments': assignments,
    })



@login_required
def take_attendance(request, course_id):
    course = Course.objects.get(id=course_id)
    students = Student.objects.filter(course=course)

    AttendanceFormSet = modelformset_factory(Attendance, fields=('student', 'present'), extra=0)

    today = timezone.now().date()

    initial_data = []
    for student in students:
        attendance, created = Attendance.objects.get_or_create(
            student=student,
            course=course,
            date=today,
            defaults={'present': False}
        )
        initial_data.append({'student': student, 'present': attendance.present})

    if request.method == 'POST':
        formset = AttendanceFormSet(request.POST, queryset=Attendance.objects.filter(course=course, date=today))
        if formset.is_valid():
            formset.save()
            return redirect('attendance_success')
        else:
            print(formset.errors)  # <-- Add this line

    else:
        formset = AttendanceFormSet(queryset=Attendance.objects.filter(course=course, date=today))

    return render(request, 'core/take_attendance.html', {
        'formset': formset,
        'course': course,
        'date': today
    })

def attendance_success(request):
    return render(request, 'core/attendance_success.html')



@login_required
def add_assignment(request):
    # Only staff (instructors) should add assignments - simple check here
    if not request.user.is_staff:
        return HttpResponseForbidden("Only instructors can add assignments.")

    if request.method == 'POST':
        form = AssignmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('assignment_list')
    else:
        form = AssignmentForm()

    return render(request, 'core/add_assignment.html', {'form': form})

# @login_required
# def assignment_list(request):
#     assignments = Assignment.objects.all()

#     # Build a dictionary: {assignment_id: submission}
#     submission_status = {}
#     submissions = AssignmentSubmission.objects.filter(student=request.user.student)
#     submissions_dict = {sub.assignment_id: sub for sub in submissions}

#     for assignment in assignments:
#         submission_status[assignment.id] = submissions_dict.get(assignment.id)

#     return render(request, 'core/assignment_list.html', {
#         'assignments': assignments,
#         'submission_status': submission_status
#     })

@login_required
def assignment_list(request):
    if hasattr(request.user, 'student'):
        submissions = AssignmentSubmission.objects.filter(student=request.user.student)
    else:
        submissions = AssignmentSubmission.objects.none()

    assignments = Assignment.objects.all()

    # Build a dictionary: {assignment_id: submission}
    submission_status = {s.assignment.id: s for s in submissions}

    return render(request, 'core/assignment_list.html', {
        'assignments': assignments,
        'submissions': submissions,
        'submission_status': submission_status,  # ✅ Pass this to the template
    })

@login_required
def submit_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    student = get_object_or_404(Student, user=request.user)

    if request.method == 'POST':
        form = AssignmentSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.assignment = assignment
            submission.student = student
            submission.save()
            return redirect('assignment_list')
    else:
        form = AssignmentSubmissionForm()

    return render(request, 'core/submit_assignment.html', {
        'form': form,
        'assignment': assignment
    })


@login_required
def grade_submission(request, submission_id):
    if not request.user.is_staff:
        return redirect('dashboard')

    submission = get_object_or_404(AssignmentSubmission, pk=submission_id)
    if request.method == 'POST':
        grade = request.POST.get('grade')
        feedback = request.POST.get('feedback')

        submission.grade = grade
        submission.feedback = feedback
        submission.save()

        return redirect('assignment_submissions', assignment_id=submission.assignment.id)

    return render(request, 'core/grade_submission.html', {
        'submission': submission,
    })


@login_required
def assignment_submissions(request, assignment_id):
    if not request.user.is_staff:
        return redirect('dashboard')  # only teachers can view

    assignment = get_object_or_404(Assignment, pk=assignment_id)
    submissions = assignment.assignmentsubmission_set.all()

    return render(request, 'core/assignment_submissions.html', {
        'assignment': assignment,
        'submissions': submissions,
    })


@login_required
def dashboard(request):
    if request.user.is_staff:
        assignments = Assignment.objects.all()
    else:
        assignments = Assignment.objects.all()  # Or filter by student class if implemented

    return render(request, 'core/dashboard.html', {
        'assignments': assignments,
    })

from django.forms import modelformset_factory

@login_required
def student_attendance(request):
    student = request.user.student
    attendance_records = Attendance.objects.filter(student=student).order_by('-date')
    return render(request, 'core/student_attendance.html', {
        'attendance_records': attendance_records,
    })


@login_required
def mark_notifications_read(request):
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return JsonResponse({'status': 'success'})

from datetime import date
from django.contrib import messages

@login_required
def mark_attendance(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    students = Student.objects.filter(course=course)

    if request.method == 'POST':
        attendance_date = date.today()

        for student in students:
            status = request.POST.get(f'status_{student.id}')
            if not status:
                messages.error(request, f"Attendance status missing for {student.user.get_full_name()}")
                return redirect(request.path)  # or reload the form

            Attendance.objects.update_or_create(
                student=student,
                date=attendance_date,
                defaults={'status': status}
            )

        messages.success(request, 'Attendance marked successfully.')
        return redirect('teacher_dashboard')  # redirect to a relevant page after save

    return render(request, 'core/mark_attendance.html', {'course': course, 'students': students})

@login_required
def student_attendance(request):
    student = request.user.student
    attendance_records = Attendance.objects.filter(student=student).order_by('-date')
    return render(request, 'core/student_attendance.html', {'attendance_records': attendance_records})


@login_required
def teacher_dashboard(request):
    if request.user.is_staff:
        assignments = Assignment.objects.all()
        return render(request, 'core/teacher_dashboard.html', {'assignments': assignments})
    else:
        return redirect('student_dashboard')


@login_required
def student_dashboard(request):
    if request.user.is_staff:
        return redirect('teacher_dashboard')

    student = request.user.student
    total = Attendance.objects.filter(student=student).count()
    present = Attendance.objects.filter(student=student, status='Present').count()
    absent = Attendance.objects.filter(student=student, status='Absent').count()
    
    return render(request, 'core/student_dashboard.html', {
        'total': total,
        'present': present,
        'absent': absent,
    })



@login_required
def attendance_page(request):
    # For now, just render a simple page
    return render(request, 'core/attendance.html')

@login_required
def assignment_detail(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    return render(request, 'core/assignment_detail.html', {'assignment': assignment})
