#-*- coding: utf-8 -*-
# py-coding-simplifer by Wanjo 20220504

from __future__ import print_function # for py2
_print=print

from time import time as now, mktime, sleep, ctime

_ = {'_':now()}

#exec('def tryx(l,e=print):\n try:return l()\n except Exception as ex:return ex if True==e else e(ex) if e else None')
def tryx(l,e=print):
    try: return l()
    except Exception as ex: return ex if True==e else e(ex) if e else None

import sys
argv = sys.argv
argc = len(argv)

import os
touch_dir = lambda fn:os.makedirs(fn,exist_ok=True)
file_exists = os.path.exists
#get_mtime = lambda f:ctime(os.path.getmtime(f))
get_mtime = lambda f:os.path.getmtime(f)

evalx = eval #lambda s:eval(s)
flag_py2 = sys.version_info.major==2
sys_import = __import__
sys_reload = __builtins__.reload if flag_py2 else sys_import('importlib').reload
reloadx = evalx('reload') if flag_py2 else sys_import('importlib').reload
refresh = lambda n:sys_reload(sys_import(n))
#def refresh(n=__name__): # del and load
#    try: del sys.modules[n]
#    finally: return sys_import(n)
def delx(o,k):
    tryx(lambda:o.__delitem__(k),False)
    tryx(lambda:o.__delattr__(k),False)
    return o

import json
class MyJsonEncoder(json.JSONEncoder):
    def default(self, obj): return tryx(lambda:json.JSONEncoder.default(self,obj),str)
s2o = lambda s:tryx(lambda:json.loads(s),False)
o2s = lambda o,indent=None:tryx(lambda:json.dumps(o, indent=indent, ensure_ascii=False, cls=MyJsonEncoder))
def get_urlopen():
  if flag_py2: from urllib2 import urlopen
  else: from urllib.request import urlopen
  return urlopen

wc=lambda u=None, data=None, m='POST',timeout=10:tryx(lambda:get_urlopen()(url=u,data=data.encode('utf-8') if isinstance(data,str) else o2s(data).encode('utf-8') if data else None,timeout=timeout).read().decode())

# NOTES: one-off call, not for performance usage!!
def wsc(u,data):
  import websocket
  s=data.encode('utf-8') if isinstance(data,str) else o2s(data).encode('utf-8') if data else None
  ws = websocket.create_connection(u)
  ws.send(s)
  rt = ws.recv() #.decode() TODO
  #ws.close()
  return rt

read = lambda f,m='r',encoding='utf-8':open(f,m,encoding=encoding).read()
write = lambda f,s,m='w',encoding='utf-8':open(f,m,encoding=encoding).write(s)
load = lambda f:s2o(read(f))
save = lambda f,o:write(f,o2s(o))

import marshal,types
dumps_func = lambda func:marshal.dumps(func.__code__)
loads_func = lambda codes,ctx,name=None:types.FunctionType(marshal.loads(codes),ctx,name=name)
func2file = lambda fc,fn:write(fn,dumps_func(fc),'wb',None)
file2func = lambda fn,ctx=globals(),name=None:types.FunctionType(marshal.loads(read(fn,'rb',None)),ctx,name=name)

class obj(dict):# dict+
    def __init__(self,pa=None):
        for k in pa or {}:self[k]=pa[k]
    def __getitem__(self,key): return self.get(key)
    def __getattr__(self,key): return self[key]
    def __setattr__(self,k,v): self[k]=v
class dict1(dict):# dict[]
    def __getitem__(self,k): return self.get(k)
class dict2(dict):# dict[][]
    def __getitem__(self,k):
        v = self.get(k)
        if v is None: self[k] = v = dict1()
        return v

class probe:# cool
    def __init__(self,ev): self._ev=ev
    def __getattr__(self,k): return self._ev(k)
    #def __setattr__(self,k,v):self[k]=v # todo
#myself = probe(lambda k:eval(k))

def hook_quit(on_quit):
    import signal
    signal.signal(signal.SIGINT, on_quit)
    if sys.platform != 'win32': signal.signal(signal.SIGHUP, on_quit)
    signal.signal(signal.SIGTERM, on_quit)

sgn = lambda v:1 if v>0 else -1 if v<0 else 0
lvl = lambda v,d=0.05:round(v/d-sgn(v)*0.5) #level to zero by d
almost = lambda v1,v2,epsilon=0.0001:abs(v1-v2)<epsilon

# tips: for HH:MM:SS, days should be 1970 ;)
def time_maker(days=0,date=None,outfmt=None,infmt='%Y-%m-%d',
        months=0):
    from datetime import datetime,timedelta
    from time import mktime
    if date is None: _dt = datetime.now()
    else: _dt = datetime.fromtimestamp(int(date))\
        if infmt=='0' or not infmt\
        else datetime.strptime(str(date),infmt)
    if months>0 or months<0:
        from dateutil.relativedelta import relativedelta
        _dt += relativedelta(months=months)
    _dt += timedelta(days=days)
    if outfmt is None: outfmt = infmt
    if outfmt=='0' or not outfmt:
        return int(mktime(_dt.timetuple()))
    return _dt.strftime(outfmt)

# alias for old codes ;)
time_add = time_maker

#e.g. acct_num = re_match(r'\D*(\d*)',str(acct))
import re
re_match=lambda p,s,a=re.M|re.I:(re.search(p, s, a) or [None,None])[1]
#e.g. re_replace(r'\D+','?',r'test 1234 ok')
re_replace=lambda p,needle,hay,a=re.M|re.I:re.sub(p, needle, hay, a)

def tiny_email(user, mypass, sender, receiver, Subject, html, smtp_host='smtp.qq.com', smtp_port=465, Cc='', Bcc=''):
    import smtplib
    from email.mime.text import MIMEText
    msg=MIMEText(html,'html','utf-8')
    msg['From'] = sender
    if type(receiver) is str:
        receiver_a = [receiver,]
        receiver_s = receiver
    else:#iterable
        receiver_a = receiver
        receiver_s = ';'.join([str(v) for v in receiver])
    msg['To'] = receiver_s
    msg['Subject']= Subject
    msg['Cc'] = Cc
    msg['Bcc'] = Bcc
    receiver_a += [Cc,Bcc]

    server=smtplib.SMTP_SSL(smtp_host, smtp_port) 
    server.login(user, mypass)
    server.sendmail(sender, receiver_a, msg.as_string())
    server.quit()

import multiprocessing
def parallel(func, a, mode='default', pool_size=None, chunksize=None):
  proc_name = multiprocessing.current_process().name
  if mode in ['loky','multiprocessing'] and proc_name!='MainProcess':
    print(f'Skip mode-{mode} for {proc_name}, call on MainProcess suggested')
    return []
  #print(f'proc_name={proc_name}')

  if pool_size is None:
    from os import cpu_count
    pool_size =  cpu_count()

  if mode == 'loky': 
    from joblib import Parallel,delayed
    return Parallel(n_jobs=pool_size,backend=mode)(delayed(func)(*v) for v in a)
  if mode == 'multiprocessing':
    Pool = multiprocessing.Pool
  else:
    from multiprocessing.dummy import Pool
  return Pool(pool_size).map(func, a)
  #with Pool(pool_size) as pool:
  #  return pool.map(func, a, chunksize=chunksize)

def mygc():
    import gc
    import sys
    # gc-patch for win32
    if sys.platform=='win32':
        # https://stackoverflow.com/questions/31851848/python-program-memory-in-windows
        import ctypes
        from ctypes import wintypes
        kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

        def errcheck_bool(result, func, args):
            if not result: raise ctypes.WinError(ctypes.get_last_error())
            return args

        kernel32.GetCurrentProcess.restype = wintypes.HANDLE
        kernel32.SetProcessWorkingSetSize.errcheck = errcheck_bool
        kernel32.SetProcessWorkingSetSize.argtypes = (wintypes.HANDLE,
                                                      ctypes.c_size_t,
                                                      ctypes.c_size_t)
        hProcess = kernel32.GetCurrentProcess()
        kernel32.SetProcessWorkingSetSize(hProcess, -1, -1)
    elif sys.platform=='linux':
        from ctypes import cdll, CDLL
        try:
            cdll.LoadLibrary("libc.so.6")
            libc = CDLL("libc.so.6")
            libc.malloc_trim(0)
        except (OSError, AttributeError):
            libc = None
    gc.collect()
    return len(gc.get_objects())

def md5(s):
  import hashlib
  return hashlib.md5(bytes(s,encoding='utf8')).hexdigest()

def yielder(func,wrap=tryx,do_yield=True): yield (wrap(func) if wrap else func())
def yielder_loop(func,wrap=tryx,do_yield=True):
  while True:
    rt = yield from yielder(func, wrap, do_yield)
    if do_yield and rt is not None: yield rt

import threading
try_async=lambda func:threading.Thread(target=func).start()

def build_address(arg1,arg2=None,folder='../tmp/'):
  port = tryx(lambda:int(arg1),False)
  if port is None:
    if sys.platform=='win32':
      host = '.' if arg2 is None else arg2
      address = rf'\\{host}\pipe\{argv[1]}'
    else:
      address = f'{folder}/{argv[1]}.sck'
  else:
    host = '127.0.0.1' if arg2 is None else arg2
    address = (host,port)
  return address


