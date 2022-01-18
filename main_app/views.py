from django.shortcuts import render
from django.http import HttpResponse

from . import uploader
from . import invoker
from . import searcher
from .models import Files
from .apps import MainAppConfig

import json

# Create your views here.
def index(request):
    return render(request, 'index.html')


def upload(request):
    return render(request, 'upload.html')


def uploadCUB(request):
    numData = int(request.POST['numData'])
    max_num = 11188
    messages = ["-Uploading Done-"]

    if numData > max_num or numData < 0:
        messages.append("[ERROR] Invalid input")
        return render(request, 'upload.html', {'messages': messages})
    else:
        messages.append(f"[Start Uploading] Uploading {numData} Files")
    
    try:
        messages.append(uploader.uploadCUB(numData))
    except:
        messages.append("[ERROR] Files are already uploaded. Old files deleted and upload begins again")
        uploader.deleteCUB()
        messages.append(uploader.uploadCUB(numData))

    return render(request, 'upload.html', {'messages': messages})


def uploadTREC(request):
    numData = int(request.POST['numData'])
        
    max_num = 192459
    messages = ["-Uploading Done-"]

    if numData > max_num or numData < 0:
        messages.append("[ERROR] Invalid input")
        return render(request, 'upload.html', {'messages': messages})
    else:
        messages.append(f"[Start Uploading] Uploading {numData} Files")
    
    try:
        messages.append(uploader.uploadTREC(numData))
    except:
        messages.append("[ERROR] Files are already uploaded. Old files deleted and upload begins again")
        uploader.deleteTREC()
        messages.append(uploader.uploadTREC(numData))

    return render(request, 'upload.html', {'messages': messages})


def invoke(request):
    events = json.loads(request.body.decode('utf-8'))
    for event in events:
        invoker.invoke(event)
    return HttpResponse(status=200)
    

def queryHistory(request):
    try:
        user = request.GET.get('user')
        path = request.GET.get('path')
    except:
        user = None
        path = None

    messages = []
    if user is not None and path is not None:
        messages = invoker.queryHistory(user, path)
        return render(request, 'queryHistory.html', {'messages': messages})
    else:
        return render(request, 'queryHistory.html', {'messages': None})    


def queryData(request):
    return render(request, 'queryData.html')


def queryDataCUB(request):
    attributeSearchTable = dict(MainAppConfig.attributeSearchTable)
    try:
        query_list = dict(request.POST)['query']
        query_list, documents = searcher.search_query_cub(query_list)
        return render(request, 'queryDataCUB.html', {'attributeSearchTable': attributeSearchTable, 'queries': query_list, 'documents': documents})
    except:
        return render(request, 'queryDataCUB.html', {'attributeSearchTable': attributeSearchTable})


def queryDataTREC(request):
    try:
        query = request.GET.get('query_searching')
    except:
        query = None

    if query is not None:
        documents = searcher.search_query_trec(request, query)
        return render(request, 'queryDataTREC.html', {'documents': documents})
    else: 
        return render(request, 'queryDataTREC.html', {'documents': None})


def queryDataCUBResult(request):
    query_list = dict(request.POST)['query']
    image_list = searcher.search_query_cub(query_list)
    return render(request, 'queryDataCUBResult.html', {"images" : image_list})
    # try:
    #     query = request.POST
    # except:
    #     query = None

    # if query is not None:
    #     documents = searcher.search_query_trec(request, query)
    #     return render(request, 'queryDataCUBResult.html', {'documents': documents})
    # else: 
    #     return render(request, 'queryDataCUBResult.html', {'documents': None})