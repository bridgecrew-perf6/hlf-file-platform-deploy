import os
import hdfs
import threading
import json
import time
import csv
from .models import Files
from .apps import MainAppConfig

port = 10871
# port = 9870

def uploadCUB(numData=11188, num_threads=3):
    start_time = time.perf_counter()

    client = hdfs.InsecureClient('http://sun01:'+str(port), user='jjlee')

    interval = int(11188 / numData)
    
    for i in range(numData):
        client.upload("/user/jjlee/CUB/", os.getcwd()+"/rawdata/CUB/" + MainAppConfig.images[i * interval])
        printProgressBar(i+1, numData, prefix="Progress:", suffix="Complete", length=50)
    end_time = time.perf_counter()
    total_time = round(end_time-start_time, 2)
    print(f"Upload finished in {total_time} seconds")

    return f"[LOG] Upload finished in {round(time.perf_counter()-start_time, 2)} seconds"

def deleteCUB():
    client = hdfs.InsecureClient('http://sun01:'+str(port), user='jjlee')
    client.delete("/user/jjlee/CUB", recursive=True)
    client.makedirs("/user/jjlee/CUB")

    print("CUB data flushed")

def uploadTREC(numData):
    start_time = time.perf_counter()
    client = hdfs.InsecureClient('http://sun01:'+str(port), user='jjlee')

    length = 50
    filler = '█'
    prefix = "Progress:"
    suffix = "Complete"
    interval = int(11188 / numData)

    with open(os.getcwd() + "/rawdata/TREC/collection_covid19_v2.tsv", 'r') as f:
        csvReader = csv.reader(f, delimiter='\t')
        cnt = 0
        for row in csvReader:
            if cnt >= numData:
                break
            data = {"id": row[0], "title": row[1], "abstract": row[2]}
            client.write("/user/jjlee/TREC/" + data['id'] + ".json", data=json.dumps(data), encoding="utf-8")
            cnt += 1
            if cnt % 10 == 0:
                print("count : ", cnt)

    return f"[LOG] Upload finished in {round(time.perf_counter()-start_time, 2)} seconds"

def deleteTREC():
    client = hdfs.InsecureClient('http://sun01:'+str(port), user='jjlee')
    client.delete("/user/jjlee/TREC", recursive=True)
    client.makedirs("/user/jjlee/TREC")

    print("deleted")

def printProgressBar(iteration, total, prefix='', suffix='', decimals=1, length = 50, fill = '█', printEnd = "\r"):
    # Source: https://stackoverflow.com/questions/3173320/text-progress-bar-in-terminal-with-block-characters
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()