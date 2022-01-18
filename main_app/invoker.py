import os
import time
import json
import pickle
from collections import defaultdict
from threading import Thread, Lock
from Naked.toolshed.shell import execute_js, muterun_js


class ThreadWithReturnValue(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)

    def join(self):
        Thread.join(self)
        return self._return


def runInvokeHistory(key, value):
  loop_cnt = 0
  while True:
    loop_cnt += 1
    ret = muterun_js("./hlf_application/application-javascript/invokehistory.js %s \'%s\'" %(key, value))
    if ret.exitcode == 0:
      # print("[SUCCS]\n" + ret.stdout.decode("utf-8"))
      break
    else :
      # print("[ERROR] " + ret.stderr.decode("utf-8"))
      if loop_cnt == 15 :
        return False
    time.sleep(1)
  return True


def runQueryHistory(user, path):
  loop_cnt = 0
  while True:
    loop_cnt += 1
    ret = muterun_js("./hlf_application/application-javascript/queryhistory.js %s %s" %(user, path))
    if ret.exitcode == 0:
      return "[Query Success]\n" + ret.stdout.decode("utf-8")
    else :
      print("[ERROR] " + ret.stderr.decode("utf-8"))
      if loop_cnt == 15 :
        return "[ERROR] " + ret.stderr.decode("utf-8")
    time.sleep(1)


def invoke(event):
  '''
  For an event, submit the history transaction and update search index from metadata file.
  '''
  key = json.dumps(event['key'])
  new_value = []
  for v in event['value']:
    new_v = {}
    new_v["type"] = v["type"]
    new_v["timestamp"] = v["timestamp"]
    new_v["detail"] = v["detail"]
    new_value.append(new_v)
  new_value = json.dumps(new_value)

  historyInvoker = ThreadWithReturnValue(target=runInvokeHistory, args=(key, new_value))
  historyInvoker.start()
  
  filename = key.split('|')[1].split('/')[-1]

  result1 = " -- "
  if historyInvoker.join():
    result1 = "OK  "
  else:
    result1 = "Err "

  return f"Transaction Invoke : {result1}"

  
def queryHistory(user, path):
  historyQuery = ThreadWithReturnValue(target=runQueryHistory, args=(user, path))
  historyQuery.start()
  return historyQuery.join().split('\n')