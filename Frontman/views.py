from django.shortcuts import render

def index(request):
    return render(request, 'Frontman/index.html')

def about(request):
    return render(request, 'Frontman/about.html')