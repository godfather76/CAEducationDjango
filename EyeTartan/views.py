from django.shortcuts import render

def index(request):
    return render(request, 'EyeTartan/index.html')

def notebooks(request):
    return(render, 'EyeTartan/notebooks.html')

def tartan_explore(request):
    return render(request, 'EyeTartan/notebooks/TartanExplore.html')

def tartan_explore_image_gen(request):
    return render(request, 'EyeTartan/notebooks/TartanExploreImageDataGen.html')

