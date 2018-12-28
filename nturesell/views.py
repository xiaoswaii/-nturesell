from django.shortcuts import render, redirect   # 加入 redirect 套件
from django.contrib.auth import authenticate
from django.contrib import auth
from django.http import HttpResponse
from django.contrib.auth.models import User as AbstractUser
from users.models import User, Product, Message, Comment, UserProfile, ChatRoom
from users.form import UploadProductForm, UploadProfileForm
from django.contrib.auth.decorators import login_required
from itertools import chain
import hashlib


@login_required
def home(request):
    if 'searchproduct' in request.POST:
        productname = request.POST["productname"]
        products1 = Product.objects.filter(productname__icontains=productname)
        products2 = Product.objects.filter(information__icontains=productname)
        products = (list(set(chain(products1, products2))))
    else:
        products = Product.objects.all()
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
                user = AbstractUser.objects.filter(username=uname)
            except:
                user = None

            if user is not None:
                message = "Username used by another"
                return render(request, "login.html", locals())
            else:
                user = AbstractUser.objects.create_user(
                    username=username, password=password)
                userinfo = User.objects.create(
                    user=user, nickname=nickname, ntumail=ntumail)
                userinfo.save()
        else:
            message = "confirm password is different from password"
            return render(request, "login.html", locals())
    return render(request, "login.html", locals())


def authenticate(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = auth.authenticate(username=username, password=password)
        if user is not None and user.is_active:
            auth.login(request, user)
            return redirect('home')
        else:
            message = "Username or password wrong"
            return render(request, "login.html", locals())

    return render(request, "home.html", locals())


def login(request):
    if request.method == "POST":
        try:
            if request.POST['submit-type'] == "Log In":
                return authenticate(request)
            elif request.POST['submit-type'] == "Register Now":
                return register(request)
        except:
            message = "account or password is wrong!!"
    return render(request, "login.html", locals())


@login_required
def profile(request):
    if 'submit' in request.POST:
        if (UserProfile.objects.filter(user_id=request.user.pk).exists()):
            oldavatar = UserProfile.objects.filter(user_id=request.user.pk)
            oldavatar.delete()
        form = UploadProfileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()

    elif 'searchproduct' in request.POST:
        productname = request.POST["productname"]
        products1 = Product.objects.filter(
            productname__icontains=productname, seller__username=request.user.username)
        products2 = Product.objects.filter(
            information__icontains=productname, seller__username=request.user.username)
        products = (list(set(chain(products1, products2))))
        return render(request, 'selldisplay.html', locals())

    elif 'whatisell' in request.POST:
        products = Product.objects.filter(
            seller__username=request.user.username)
        return render(request, 'selldisplay.html', locals())

    if request.user.is_authenticated:
        profile = User.objects.get(user__id=request.user.pk)
        if UserProfile.objects.filter(user__id=request.user.pk).exists():
            avatar = UserProfile.objects.get(
                user_id=request.user.pk)
        return render(request, 'profile.html', locals())
    return render(request, 'profile.html', locals())


@login_required
def sell(request):
    if request.method == "POST":
        form = UploadProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
    return render(request, 'sell.html', locals())


def logout(request):
    auth.logout(request)
    return redirect('/register')


@login_required
def chat(request):
    if 'search' in request.POST:
        searchname = request.POST["searchname"]
        if searchname:
            searchuserresult = User.objects.filter(
                user__username__contains=searchname)
            return render(request, 'chat.html', locals())
        else:
            return render(request, 'chat.html', locals())

    if 'talkto' in request.POST:
        sender = request.user.username
        receiver = request.POST['receiver']
        conversation1 = Message.objects.filter(
            sent_from__username=sender, sent_to__username=receiver)
        conversation2 = Message.objects.filter(
            sent_to__username=sender, sent_from__username=receiver)
        conversation = list(chain(conversation1, conversation2))
        conversation.sort(key=lambda x: x.date)
        if UserProfile.objects.filter(user_id=request.user.pk).exists():
            avatar = UserProfile.objects.get(user_id=request.user.pk)

        user2 = AbstractUser.objects.get(username=receiver)

        # find the chat room
        roomName = ""
        if ChatRoom.objects.filter(user1__username=sender, user2__username=receiver).exists():
            roomName = ChatRoom.objects.get(
                user1__username=sender, user2__username=receiver).room_name
        elif ChatRoom.objects.filter(user2__username=sender, user1__username=receiver).exists():
            roomName = ChatRoom.objects.get(
                user2__username=sender, user1__username=receiver).room_name
        else:
            roomName = hashlib.sha256((sender + receiver).encode()).hexdigest()
            ChatRoom.objects.create(
                user1=request.user, user2=user2, room_name=roomName)

        return redirect('/chat/' + roomName + '/', locals())
    if 'talking' in request.POST:
        sender = request.user.username
        sent_from = AbstractUser.objects.get(username=request.user.username)
        sent_too = request.POST['receiver']
        receiver = sent_too
        sent_to = AbstractUser.objects.get(username=sent_too)
        talk = request.POST['talk']
        if talk:
            Message.objects.create(sent_from=sent_from,
                                   sent_to=sent_to, msg=talk)
            conversation1 = Message.objects.filter(
                sent_from__username=sender, sent_to__username=sent_too)
            conversation2 = Message.objects.filter(
                sent_to__username=sender, sent_from__username=sent_too)
            conversation = list(chain(conversation1, conversation2))
            conversation.sort(key=lambda x: x.date)
            return render(request, 'chatroom.html', locals())
        else:
            conversation1 = Message.objects.filter(
                sent_from__username=sender, sent_to__username=receiver)
            conversation2 = Message.objects.filter(
                sent_to__username=sender, sent_from__username=receiver)
            conversation = list(chain(conversation1, conversation2))
            conversation.sort(key=lambda x: x.date)
            return render(request, 'chatroom.html', locals())
    searchuserresult = User.objects.all()
    return render(request, 'chat.html', locals())


@login_required
def productdetail(request):
    if 'commenting' in request.POST:
        commenter = AbstractUser.objects.get(username=request.user.username)
        comment = request.POST['comment']
        productpk = request.POST['productpk']
        Comment.objects.create(commenter=commenter,
                               productpk=productpk, comment=comment)
        products = Product.objects.get(id=productpk)
        comment = Comment.objects.filter(productpk=productpk)
        return render(request, 'productdetail.html', locals())
    if request.method == "POST":
        productpk = request.POST["productpk"]
        products = Product.objects.get(id=productpk)
        comment = Comment.objects.filter(productpk=productpk)
        return render(request, 'productdetail.html', locals())
    return render(request, 'productdetail.html', locals())
