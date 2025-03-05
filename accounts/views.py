from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import CustomUser, BlogPost, Appointment
from django.contrib.auth.decorators import login_required
import datetime
from datetime import datetime, timedelta
from .google_calendar import create_google_calendar_event
from django.conf import settings

def signup(request):
    if request.method == "POST":
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        user_type = request.POST['user_type']
        address_line1 = request.POST['address_line1']
        city = request.POST['city']
        state = request.POST['state']
        pincode = request.POST['pincode']
        profile_picture = request.FILES.get('profile_picture')

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect('signup')

        user = CustomUser.objects.create_user(
            username=username, email=email, password=password,
            first_name=first_name, last_name=last_name, user_type=user_type,
            address_line1=address_line1, city=city, state=state, pincode=pincode,
            profile_picture=profile_picture
        )
        user.save()
        messages.success(request, "Signup successful! Please login.")
        return redirect('login')

    return render(request, "signup.html")


def user_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            if user.user_type == "doctor":
                return redirect("doctor_dashboard")
            else:
                return redirect("patient_dashboard")
        else:
            messages.error(request, "Invalid Credentials!")
            return redirect("login")

    return render(request, "login.html")

@login_required
def doctor_dashboard(request):
    return render(request, "doctor_dashboard.html", {"user": request.user})

@login_required
def patient_dashboard(request):
    return render(request, "patient_dashboard.html", {"user": request.user})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def create_blog(request):
    if request.user.user_type != "doctor":
        messages.error(request, "Only doctors can create blogs.")
        return redirect("view_blogs")

    if request.method == "POST":
        title = request.POST.get("title")
        category = request.POST.get("category")
        summary = request.POST.get("summary")
        content = request.POST.get("content")
        is_draft = request.POST.get("is_draft") == "on"
        image = request.FILES.get("image")

        blog_post = BlogPost.objects.create(
            title=title,
            category=category,
            summary=summary,
            content=content,
            image=image,
            is_draft=is_draft,
            author=request.user,
        )
        blog_post.save()
        return redirect("view_blogs")

    return render(request, "create_blog.html")


@login_required
def view_blogs(request):
    filter_my_blogs = request.GET.get("my") == "true"

    if filter_my_blogs:
        if request.user.user_type != "doctor":
            messages.error(request, "Only doctors can access their own blogs.")
            return redirect("view_blogs")

        blogs = BlogPost.objects.filter(author=request.user, is_draft=False)
        heading = "My Published Blogs"
    else:
        blogs = BlogPost.objects.filter(is_draft=False)
        heading = "All Published Blogs"

    return render(request, "view_blogs.html", {"blogs": blogs, "heading": heading})


@login_required
def list_doctors(request):
    doctors = CustomUser.objects.filter(user_type="doctor")  # Assuming `user_type` field exists
    return render(request, "list_doctors.html", {"doctors": doctors})


@login_required
def book_appointment(request, doctor_id):
    doctor = get_object_or_404(CustomUser, id=doctor_id, user_type="doctor")

    if request.method == "POST":
        specialty = request.POST.get("specialty")
        date_str = request.POST.get("date")
        start_time_str = request.POST.get("start_time")

        try:
            appointment_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            start_datetime = datetime.strptime(f"{date_str} {start_time_str}", "%Y-%m-%d %H:%M")
            end_datetime = start_datetime + timedelta(minutes=45)
        except ValueError:
            messages.error(request, "Invalid date or time format.")
            return render(request, "book_appointment.html", {"doctor": doctor})

        # **Check if doctor is available**
        existing_appointment = Appointment.objects.filter(
            doctor=doctor,
            date=appointment_date,
            start_time__lt=end_datetime.time(),
            end_time__gt=start_datetime.time()
        ).exists()

        if existing_appointment:
            messages.error(request, "This time slot is already booked. Please choose another time.")
            return render(request, "book_appointment.html", {"doctor": doctor})

        # **Save appointment**
        appointment = Appointment.objects.create(
            patient=request.user,
            doctor=doctor,
            specialty=specialty,
            date=appointment_date,
            start_time=start_datetime.time(),
            end_time=end_datetime.time()
        )

        # **Create Google Calendar Event**
        event_link = None
        try:
            event_link = create_google_calendar_event(appointment)
        except Exception as e:
            print("Google Calendar API Error:", str(e))
            messages.warning(request, "Appointment booked, but failed to sync with Google Calendar.")

        print(event_link)
        messages.success(request, f"Appointment booked! View in Calendar: {event_link if event_link else 'Not Available'}")
        return redirect("user_appointments")

    return render(request, "book_appointment.html", {"doctor": doctor})



@login_required
def user_appointments(request):
    if request.user.user_type == "doctor":
        # Fetch appointments where the logged-in user is the doctor
        appointments = Appointment.objects.filter(doctor=request.user).order_by("date", "start_time")
    else:
        # Fetch appointments where the logged-in user is the patient
        appointments = Appointment.objects.filter(patient=request.user).order_by("date", "start_time")
    
    return render(request, "appointment_details.html", {"appointments": appointments})
