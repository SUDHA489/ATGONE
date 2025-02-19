from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import CustomUser

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


def doctor_dashboard(request):
    return render(request, "doctor_dashboard.html", {"user": request.user})

def patient_dashboard(request):
    return render(request, "patient_dashboard.html", {"user": request.user})