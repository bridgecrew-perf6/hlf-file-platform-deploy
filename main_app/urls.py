"""ERC_deploy URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload, name='upload'),
    path('uploadCUB/', views.uploadCUB, name='uploadCUB'),
    path('uploadTREC/', views.uploadTREC, name='uploadTREC'),
    path('invoke/', views.invoke, name='invoke'),
    path('queryHistory/', views.queryHistory, name='queryHistory'),
    path('queryData/', views.queryData, name='queryData'),
    path('queryDataCUB/', views.queryDataCUB, name='queryDataCUB'),
    path('queryDataTREC/', views.queryDataTREC, name='queryDataTREC'),
    path('queryDataCUBResult/', views.queryDataCUBResult, name='queryDataCUBResult'),
]
