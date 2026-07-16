from django.contrib.gis import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('Frontman.urls')),
    path('CalEd/', include('CalEd.urls')),
    path('EyeTartan/', include('EyeTartan.urls')),

]
