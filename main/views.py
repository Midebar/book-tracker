import datetime
import json

from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound, JsonResponse
from django.core import serializers
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse

from .forms import BookForm
from .models import Book

def testing(request):
    return render(request, "testing.html")

@login_required(login_url='/login')
def show_main(request):
    books = Book.objects.filter(user=request.user)

    context = {
        'name': request.user.username,
        'class': 'PBP A',
        'books': books,
        'last_login': request.COOKIES['last_login'],
    }

    return render(request, "main.html", context)

@login_required(login_url='/login')
def create_book(request):
    form = BookForm(request.POST or None)

    if form.is_valid() and request.method == "POST":
        book = form.save(commit=False)
        book.user = request.user
        book.save()
        return redirect('main:show_main')

    context = {'form': form}
    return render(request, "create_book.html", context)

@login_required(login_url='/login')
def edit_book(request, id):
    # Get book berdasarkan ID
    book = Book.objects.get(pk = id)

    # Set book sebagai instance dari form
    form = BookForm(request.POST or None, instance=book)

    if form.is_valid() and request.method == "POST":
        # Simpan form dan kembali ke halaman awal
        form.save()
        return HttpResponseRedirect(reverse('main:show_main'))

    context = {'form': form}
    return render(request, "edit_book.html", context)

@login_required(login_url='/login')
def delete_book(request, id):
    # Get data berdasarkan ID
    book = Book.objects.get(pk = id)
    # Hapus data
    book.delete()
    # Kembali ke halaman awal
    return HttpResponseRedirect(reverse('main:show_main'))

@csrf_exempt
def add_book_ajax(request):
    if request.method == 'POST':
        name = request.POST.get("name")
        page = request.POST.get("page")
        description = request.POST.get("description")
        user = request.user

        new_book = Book(name=name, page=page, description=description, user=user)
        new_book.save()

        return HttpResponse(b"CREATED", status=201)

    return HttpResponseNotFound()

def show_xml(request):
    data = Book.objects.all()
    return HttpResponse(serializers.serialize("xml", data), content_type="application/xml")

def show_json(request):
    data = Book.objects.all()
    return HttpResponse(serializers.serialize("json", data), content_type="application/json")

def show_xml_by_id(request, id):
    data = Book.objects.filter(pk=id)
    return HttpResponse(serializers.serialize("xml", data), content_type="application/xml")

def show_json_by_id(request, id):
    data = Book.objects.filter(pk=id)
    return HttpResponse(serializers.serialize("json", data), content_type="application/json")

def register(request):
    form = UserCreationForm()

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been successfully created!')
            return redirect('main:login')
    context = {'form':form}
    return render(request, 'register.html', context)

def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            response = HttpResponseRedirect(reverse("main:show_main"))
            response.set_cookie('last_login', str(datetime.datetime.now()))
            return response
        else:
            messages.info(request, 'Sorry, incorrect username or password. Please try again.')
    context = {}
    return render(request, 'login.html', context)

def logout_user(request):
    logout(request)
    response = HttpResponseRedirect(reverse('main:login'))
    response.delete_cookie('last_login')
    return response

@csrf_exempt
def create_book_flutter(request):
    if request.method == 'POST':

        data = json.loads(request.body)

        new_book = Book.objects.create(
            user = request.user,
            name = data["name"],
            page = int(data["page"]),
            description = data["description"]
        )

        new_book.save()

        return JsonResponse({"status": "success"}, status=200)
    else:
        return JsonResponse({"status": "error"}, status=401)