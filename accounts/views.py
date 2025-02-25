from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import CustomUser, BlogPost
from django.contrib.auth.decorators import login_required

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

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def create_blog(request):
    if request.user.user_type != "doctor":
        messages.error(request, "Only doctors can create blogs.")
        return redirect("view_blogs")  # Redirect patients to blogs page

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
