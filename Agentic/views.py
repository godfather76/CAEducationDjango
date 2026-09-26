from django.shortcuts import render

def index(request):
    return render(request, 'Agentic/index.html')