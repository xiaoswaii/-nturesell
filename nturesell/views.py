from django.shortcuts import render,redirect   # 加入 redirect 套件
from django.contrib.auth import authenticate
from django.contrib import auth
from django.http import HttpResponse
from django.contrib.auth.models import User as AbstractUser
from users.models import User
from django.contrib.auth.decorators import login_required


@login_required
def home(request):
    return render(request, 'home.html', locals())

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        nickname = request.POST["nickname"]
        ntumail = request.POST["ntumail"]
        password = request.POST["password"]
        confirmpassword = request.POST["confirm-password"]
        if(password == confirmpassword):
            try:
                user = AbstractUser.objects.filter(userame = uname)
            except:
                user = None

            if user is not None:
                message = "Username used by another"
            else:
                user = AbstractUser.objects.create_user(username = username, password = password)
                userinfo  = User.objects.create(user = user , nickname = nickname, ntumail = ntumail)
                userinfo.save()

        else:
            message= "confirm password is different from password"

    return render(request ,"login.html",locals())


def authenticate(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = auth.authenticate(username = username, password = password)
        if user is not None and user.is_active:
            auth.login(request, user)
            return render(request,"home.html", locals())
        else:
            message='尚未登入'

    return render(request,"home.html",locals())

def login(request):
    if request.method == "POST":
        try:
            if request.POST['submit-type'] == "Log In":
                return authenticate(request)
            elif request.POST['submit-type'] == "Register Now":
                return register(request)
        except:
            pass
    return render(request,"login.html",locals())

@login_required
def profile(request):
    if request.user.is_authenticated:
        print(request.user.username, "hihi")
        profile=User.objects.get(user__username__contains = request.user.username)
        return render(request,'profile.html',locals())
    return render(request,'profile.html',locals())

