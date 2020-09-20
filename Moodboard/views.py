import requests
from django.core.files.base import ContentFile
from django.shortcuts import render, HttpResponse, redirect
from . import settings
import os
from .models import TheMoodboard, Img
from .forms import UploadImgForm, TheMoodboardForm
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q
from .forms import RegistrationForm
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.core.paginator import Paginator
from django.contrib import messages
from django.urls import reverse
from .forms import UserUpdateForm
import random
import string

static_dirs = settings.STATICFILES_DIRS
media = os.path.join(os.path.join(os.path.join
                                  (os.path.join(settings.BASE_DIR,
                                                'media'), 'static'), 'moodboard'), 'images')


def index(request):
    boards = TheMoodboard.objects.filter(isPrivate=False)
    boardlist = []
    if boards:
        for board in boards:
            boardlist.append(board.picsContained.all())
    # merge resulting queryset
    queries = boardlist[0]
    for x in range(len(boardlist)):
        queries |= boardlist[x]
    paginator = Paginator(queries, 18)
    page = request.GET.get('page')
    queries = paginator.get_page(page)
    context = {'queries': queries,
               'boards': boards,
               'user': request.user
               }
    return render(request, 'moodboard/main.html', context)


def signup_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f"Account created for {username}!")
            # log the user in
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'users/signup.html', {'form': form})


def login_view(request):
    form = AuthenticationForm(data=request.POST)
    if request.method == "POST":
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome, {user}. Thanks for logging in.")
            return redirect('myboards')
        else:
            messages.error(request, "invalid login")
            form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect("login")


users_img = []


def gen_random_name():
    randomName = ''.join(random.choice(string.ascii_letters) for x in range(10)) + '.jpg'
    return randomName


def upload_picture(request, user, uplform, redirectto):
    if request.method == 'POST':
        if uplform.is_valid():
            # get field inputs
            MdbName = uplform.cleaned_data['moodboard']
            ImgName = uplform.cleaned_data['image']
            url = uplform.cleaned_data['url_img']
            # whitespace is changed to _ in database
            if ImgName or url:
                if ImgName:
                    uplform.save()
                    # adding image to moodboard. first we get image object using modelform instance
                    imageObj = uplform.instance
                    mdb_object = TheMoodboard.objects.get(projectName=MdbName, owner=user)
                    # then pass image object to our moodboard pics field
                    mdb_object.picsContained.add(imageObj)
                    if redirectto == 'userpage':
                        messages.success(request, 'Your image has been added!')
                if url:
                    name = gen_random_name()
                    imageObj = uplform.instance
                    image = requests.get(url)
                    data = ContentFile(image.content)
                    imageObj.image.save(name, data)
                    uplform.save()
                    mdb_object = TheMoodboard.objects.get(projectName=MdbName, owner=user)
                    mdb_object.picsContained.add(imageObj)
                    if redirectto == 'userpage':
                        messages.success(request, 'Your image has been added!')
            else:
                messages.error(request, 'Add image file or url')
            return redirect(redirectto)
        else:
            messages.error(request, 'Form is not valid')
    else:
        pass


def sort_by(request, method, descending=False):
    boards = TheMoodboard.objects.filter(owner=request.user.id)
    boards = boards.order_by(method)
    if descending:
        boards = boards.order_by(-method)
    myboards_view(request, order=boards)


@login_required(login_url='login')
def myboards_view(request):
    user = User.objects.get(id=request.user.id)
    uplform = UploadImgForm(user, request.POST, request.FILES)
    # getting user model of current user
    upload_picture(request, user, uplform, 'myboards')
    boards = TheMoodboard.objects.filter(owner=request.user.id)
    # optional sorting query set
    sort_name = request.GET.get('sort_name', False)
    sort_name_desc = request.GET.get('sort_name_desc', False)
    sort_date = request.GET.get('sort_date', False)
    sort_date_desc = request.GET.get('sort_date_desc', False)

    if sort_name:
        boards = boards.order_by('projectName')
    elif sort_name_desc:
        boards = boards.order_by('-projectName')
    elif sort_date:
        boards = boards.order_by('date_created')
    elif sort_date_desc:
        boards = boards.order_by('-date_created')

    context = {'uplform': uplform,
               'user': request.user,
               'boards': boards
               }

    return render(request, 'moodboard/myboards.html', context)


@login_required(login_url='login')
def new_board_view(request):
    createForm = TheMoodboardForm(request.POST)
    user = User.objects.get(id=request.user.id)
    if request.method == 'POST':
        if createForm.is_valid():
            create = createForm.save(commit=False)
            # passing user to the form
            create.owner = user
            create.save()
            return redirect('myboards')
        else:
            messages.error(request, 'Form is not valid')
    return render(request, 'moodboard/new_board.html', {'createForm': createForm})


@login_required()
def profilechange_view(request):
    user_updateform = UserUpdateForm(request.POST, instance=request.user)
    if request.method == 'POST':
        if user_updateform.is_valid():
            user_updateform.save()
            messages.success(request, 'Your account info was updated')
            return redirect('userpage')
        else:
            messages.error(request, 'Something went wrong')
    else:
        user_updateform = UserUpdateForm(instance=request.user)
    context = {
        'userUpdate': user_updateform,
    }
    return render(request, 'users/profile_change.html', context)


@login_required(login_url='login')
def userpage_view(request):
    user = User.objects.get(id=request.user.id)
    boards = TheMoodboard.objects.filter(owner=request.user.id)
    uplform = UploadImgForm(user, request.POST, request.FILES)
    upload_picture(request, user, uplform, 'userpage')

    if request.method == 'POST':
        if uplform.is_valid():
            return redirect('userpage')
    context = {
        'user': request.user,
        'user_id': request.user.id,
        'boards': boards,
        'uplform': uplform,
    }
    return render(request, 'moodboard/userpage.html', context)


@login_required()
def rename(request, board_id):
    if request.user.id == TheMoodboard.objects.filter(pk=board_id).first().owner.id:
        instance = TheMoodboard.objects.get(pk=board_id)
        form = TheMoodboardForm(request.POST or None, instance=instance)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()
            messages.success(request, 'Changes saved')
            return redirect(reverse('userpage'))
        return render(request, 'moodboard/rename.html', {'form': form})
    else:
        return HttpResponseForbidden()


@login_required()
def delete_from_moodboard(request, board_id, img_id):
    if request.user.id == TheMoodboard.objects.filter(pk=board_id).first().owner.id:
        user = User.objects.get(id=request.user.id)
        if user:
            mdbObj = TheMoodboard.objects.filter(owner=user, pk=board_id).first()
            if mdbObj:
                imageObj = Img.objects.filter(pk=img_id, moodboard=mdbObj).first()
                pic = TheMoodboard.objects.filter(picsContained=imageObj).first()
                if pic:
                    pic.picsContained.remove(imageObj)
                    key = 'static/moodboard/images/' + str(imageObj.image)
                    #s3_delete(key)
                # we can optionally delete file itself
                else:
                    messages.error(request, 'Image not found')
            else:
                messages.error(request, 'Moodboard not found')
        return redirect(reverse('myboards'))
    else:
        return HttpResponseForbidden()


image_list = []
deleted_main = []


@login_required()
def superuser_delete_from_moodboard(request, img_id):
    user = User.objects.get(id=request.user.id)
    if user.is_superuser:
        imageObj = Img.objects.filter(pk=img_id).first()
        if imageObj:
            pic = TheMoodboard.objects.filter(picsContained=imageObj).first()
            if pic:
                pic.picsContained.remove(imageObj)
                try:
                    if img_id in image_list:
                        image_list.remove(img_id)
                        deleted_main.append(img_id)
                # we can optionally delete file itself
                except ValueError:
                    pass
        else:
            messages.error(request, 'Image not found')
    else:
        messages.error(request, 'Not allowed')
    return redirect(reverse('index'))


@login_required()
def delete_moodboard(request, board_id):
    if request.user.id == TheMoodboard.objects.filter(pk=board_id).first().owner.id:
        user = User.objects.get(id=request.user.id)
        response = userpage_view(request)
        if user:
            mdbObj = TheMoodboard.objects.filter(owner=user, pk=board_id).first()
            if mdbObj:
                mdbObj.delete()
                messages.success(request, 'Moodboard deleted')
                return redirect(reverse('userpage'))
            else:
                messages.error(request, 'No such board')
                return redirect(reverse('userpage'))
    else:
        return HttpResponseForbidden()


def discover_view(request):
    boards = TheMoodboard.objects.filter(isPrivate=False)
    title_contains = request.GET.get('projectName_contains')
    title_exact = request.GET.get('projectName_exact')

    if title_contains:
        boards = boards.filter(projectName__icontains=title_contains)
        if not boards:
            users = User.objects.filter(username__icontains=title_contains)
            boards = TheMoodboard.objects.filter(Q(isPrivate=False), Q(owner__in=users))

    if title_exact:
        boards = boards.filter(projectName=title_exact)

    context = {
        'boards': boards,
    }
    return render(request, 'moodboard/discover.html', context)


def shared_view(request, share_link):
    board = TheMoodboard.objects.get(share_url=share_link)
    context = {
        'board': board,
    }
    if board:
        return render(request, 'moodboard/shared_board.html', context)
    else:
        return HttpResponse(404)


def generate_share_link(request, board_id):
    link = "".join(random.choice(string.ascii_letters) for i in range(10))
    boards = TheMoodboard.objects.filter(pk=board_id).first()
    if boards.share_url is None:
        boards.share_url = link
        boards.save()
    return redirect(reverse('userpage'))

