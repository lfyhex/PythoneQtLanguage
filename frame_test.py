# coding=gbk
#!/bin/python

import configparser
import os,os.path
import subprocess
import logging
import time
import threading
import random
import platform
import signal
import sys
from ctypes import *

config_fn = "frame_test.ini"
success_fs = []
failed_fs = []
convertor = ''
src_dir = '' # source video dir
dst_dir = '' # dest dir, all output file will be at this folder
log_dir = '' # log dir
vfile_dir = '' # converted video file dir
rep_fn = ''
rep_f = None
just_md5 = False
opts_input = ''
input_handler = ''
heartbeat_fn = ''
profile_fn = ''
test_profile = '1'
profile_holder = None
frame_rate = ''
is_exit = False

def signal_handler(signal, frame):
    global is_exit
    is_exit = True

# deal with profile
import sqlite3
class profileHolder:
    def __init__(self, fn):
        self.conn = sqlite3.connect(fn)
        self.tbl_name = 'profile_item'
        self.cursor = self.conn.cursor()
        self.interested_fields = {'format_ext':'',\
                             'video_codecs':'codec:v'}
        #{"libx264", {".mp4",".m4v"}}
        self.profile_items = {'':{'',''}}
        self.load()

    def load(self):
        fields = list(self.interested_fields.keys())
        sql = "select %s from %s" % (','.join(fields), self.tbl_name)
        rows = self.cursor.execute(sql)
        for r in rows:
            #r (".mp4", "libx264$H264")
            if r[0] and r[1]:
                format = r[0];
                vcodecs = r[1];
                codecs = vcodecs.split(",")

                for n in codecs:
                    singlecodec = n
                    realcodec = singlecodec.split("$")[0]
                    if realcodec not in self.profile_items:
                        fset = set()
                        fset.add(format)
                        self.profile_items[realcodec] = fset
                    else:
                        self.profile_items[realcodec].add(format)
        print(self.profile_items.keys())
        pass

    def construct_output_params(self, dst_fn):
        # return output args
        global frame_rate
        for vcodecs in self.profile_items:
            if vcodecs and vcodecs != '':
                for foramt in self.profile_items[vcodecs]:
                    dst_new_fn = "%s_%s%s" % (dst_fn, vcodecs, foramt)
                    dst_new_fn = dst_new_fn.replace('*', '')
                    if os.path.exists(dst_new_fn):
                        print("Need dup: %s" % dst_new_fn)
                        dst_new_fn = "%s_%s_dup_%d%s" % (dst_fn, vcodecs, random.random() * 1000.0, foramt)

                    out_params=''
                    vc = vcodecs.strip()
                    out_params += " -codec:v %s " % vc
                    out_params += " -r %s " % frame_rate
                    out_params += ' -t 3 -y %s ' % (dst_new_fn.replace('*', ''))
                    yield out_params
        return
        
    def show(self):
        print(self.profile_items)
        return
        

class checkHB(threading.Thread):
    def __init__(self, hb_fn):
        super(checkHB, self).__init__()
        self.hb_fn = hb_fn
        self.continue_chk = True

    def killConvertor_win(self):
        arr = c_ulong * 256
        lpidProcess= arr()
        cb = sizeof(lpidProcess)
        cbNeeded = c_ulong()
        cbNeeded = c_ulong()
        hModule = c_ulong()
        count = c_ulong() 
        #PSAPI.DLL
        psapi = windll.psapi
        #Kernel32.DLL
        kernel = windll.kernel32
        modname = c_buffer(300)
        PROCESS_QUERY_INFORMATION = 0x0400
        PROCESS_VM_READ = 0x0010
        PROCESS_TERMINATE = 0x0001
        #Call Enumprocesses to get hold of process id's
        psapi.EnumProcesses(byref(lpidProcess),
                            cb,
                            byref(cbNeeded)) 
        #Number of processes returned
        nReturned = int(cbNeeded.value/sizeof(c_ulong()))
        pid = [i for i in lpidProcess][:nReturned]
        for id in pid:        
            #Get handle to the process based on PID
            hProcess = kernel.OpenProcess(PROCESS_QUERY_INFORMATION|PROCESS_VM_READ|
            PROCESS_TERMINATE, False, id)
            if hProcess:
                if psapi.GetModuleFileNameExA(hProcess, 0, modname, sizeof(modname)):
                    sname = ''.join([ str(i).strip('b\'') for i in modname if i !='\x00'])
                    if convertor.split('/')[-1] in sname:
                        logging.debug("Ready to kill the convertor process")
                        kernel.TerminateProcess(hProcess, 2)
                        logging.debug("Killed the convertor process")
                        return
            pass
        return

    def killConvertor_mac(self):
        pro_ret = subprocess.check_output('ps -e | grep convertor', shell=True)
        bytes_ret = pro_ret.split(b'\n')
        for bt in bytes_ret:
            if b'grep' in bt:
                continue
            bt = bt.lstrip()
            if len(bt) == 0:
                continue
            lst = bt.split(b'\n')
            pid = str(lst[0], encoding='utf8')
            cmd = 'kill -9 %s' % pid
            print(cmd)
            subprocess.call(cmd, shell=True)

    def killConvertor(self):
        plat = platform.platform()
        if 'Window' in plat:
            self.killConvertor_win()
        else:
            self.killConvertor_mac()

    def run(self):
        last_t = 0
        stop_cnt = 0
        longest_time = 300
        interval = 2
        while self.continue_chk:
            try:
                s = os.stat(self.hb_fn)
                if last_t !=s.st_mtime:
                    last_t = s.st_mtime
                    stop_cnt = 0
                else:
                    stop_cnt += 1
            except:
                stop_cnt += 1
            if stop_cnt>(longest_time/interval):
                self.killConvertor()
                break
            time.sleep(interval)
        return
        
    def setExit(self):
        self.continue_chk = False

def invoke_convertor(cmd, log_fn):
    global heartbeat_fn
    ret = 1
    try:    
        err=open(log_fn, "w+")
        logging.debug("Ready to convert with: %s" % " ".join(cmd))
        ct = checkHB(heartbeat_fn)
        ct.start()
        ret = subprocess.call([opt.strip() for opt in cmd if opt and opt !=''], stdout=None, stderr=err)
        ct.setExit()
        ct.join(600)
        if ct.is_alive():
            logging.error("Heartbeat checking thread still alive")
    except OSError as e:
        logging.error("Got a OSError while running test case. errno: %d, err: %s" % (e.errno, e.strerror))
    except ValueError as e:
        logging.error("Got a ValueError exception while running test case")
    except subprocess.CalledProcessError as e:
        logging.error("Got a CalledProcessError exception while running test case")
    except :
        logging.error("Got a exception while running test case")
    return ret
    
    
def rename_logfile(src, ok):
    def rename_f(src, dup, ok):
        head, tail = os.path.split(src)
        base = tail
        if dup:
            base += "_dup_%d" % (random.random()*1000.0)
        if ok:
            # rename logfile to fn-succeed
            new_fn = "%s/Succeed_%s.log" % (head,base)
            os.rename(src, new_fn)
        else:
            # rename logfile to fn-failed:
            new_fn = "%s/Failed_%s.log" % (head,base)
            os.rename(src, new_fn)
        return
    try:
        rename_f(src, False, ok)
    except FileExistsError:
        rename_f(src, True, ok)
    return        
        
def convert(src_fn, dst_fn):
    global heartbeat_fn, test_profile, profile_holder, log_dir
    cmd = [convertor]
    cmd += ['-heartbeat']
    cmd += ['%s' % heartbeat_fn]
    src_fn = src_fn.replace(",", "\\,")
    if opts_input != '':
        cmd += opts_input.split(' ')
    if input_handler == '':
        cmd += ["-i", "normal=fn:%s" % src_fn]
    else:
        cmd += ["-i", "normal=raw:%s,fn:%s" % (input_handler, src_fn)]
    if profile_holder:
        print("------------test use profile-----------")
        for out_opts in profile_holder.construct_output_params(dst_fn):
            # output file name may contain ' '
            tp = out_opts.split('-y')
            real_cmd = cmd +  tp[0].split(' ')
            real_cmd += ['-y']
            if False:
                print("file already exist")
            else:
                real_cmd += [tp[1]]
                # output file may contain multiple \, .
                log_fn = "%s/%s" % (log_dir, tp[1].split('/')[-1])
                #logging.debug(log_fn)
                ret = invoke_convertor(real_cmd, log_fn)
                rename_logfile(log_fn, ret==0)
                yield ret
    else:
        print("---------test use default profile--------------")
        opts = "-strict -2 -vcodec mpeg4 -s 640x480 -b:v 1200000 -aspect 640:480 -r 29.970 -ar 44100 -ac 2 -b:a 96000 -async 1 -y"
        if just_md5:
            opts = "-strict -2 -vcodec mpeg4 -s 640x480 -b:v 1200000 -aspect 640:480 -r 29.970 -ar 44100 -ac 2 -b:a 96000 -async 1 -f md5 -y"
            pos = dst_fn.rfind(".")
            dst_fn = "md5:"+dst_fn[:pos]+".md5"
        cmd += opts.split(' ')
        cmd += ["%s" % dst_fn]
        log_fn = "%s/%s" % (log_dir, dst_fn.split('/')[-1])
        ret = invoke_convertor(cmd, log_fn)
        rename_logfile(log_fn, ret==0)
        yield ret
    return

def md5(fn):
    import hashlib
    f = open(fn, "rb")
    md = hashlib.md5()
    while 1:
        b = f.read(1024*1024)
        if len(b)>0:
            md.update(b)
        else:
            break
    return md.digest()

def testOne(src_fn, dst_fn):
    global is_exit
    start=time.time()
    tstart=time.strftime("%H:%M:%S", time.localtime())
    for ret in convert(src_fn, dst_fn):
        try:
            if is_exit:
                print("--------------user cancel----------")
                break
            end=time.time()
            tend=time.strftime("%H:%M:%S", time.localtime())
            try:
                if ret ==0:
                    rep_f.write("%s    %s    %s    %f    %s\n" % (src_fn,tstart,tend,end-start,'Yes'))
                else:
                    rep_f.write("%s    %s    %s    %f    %s\n" % (src_fn,tstart,tend,end-start,'No'))
            except UnicodeEncodeError as e:
                if ret ==0:
                    rep_f.write("%s    %s    %s    %f    %s\n" % (src_fn.decode('gb2312'),tstart,tend,end-start,'Yes'))
                else:
                    rep_f.write("%s    %s    %s    %f    %s\n" % (src_fn.decode('gb2312'),tstart,tend,end-start,'No'))
            if ret==0 and not just_md5:
                md = md5(dst_fn)
                md_fn = "%s.md5" % (dst_fn)
                f = open(md_fn, 'wb+')
                f.write(md)
                f.close()
        except:
            logging.error("Can not do some work after converting")
        pass
    return

def testDir(dir, dst):
    for f in os.listdir(dir):
        #try:
        cur_f = "%s/%s" % (dir,f)
        print(cur_f)
        if os.path.isdir(cur_f):
            dst_n = "%s/%s" % (dst, f)
            os.makedirs(dst_n, exist_ok=True)
            testDir(cur_f, dst_n)
        else:
            pos = f.rfind(".")
            #try:
            # is file exits ?
            dst_n = "%s/%s.mp4" % (dst, f[:pos])
            testOne(cur_f, dst_n)
            #except:
            #    logging.error("Some errors happended while handling this file")
        pass
        #except:
        #    logging.log("Something wrong!")
        #finally:
        #    pass
    return
    
def read_config():
    global src_dir, dst_dir, rep_f, convertor, vfile_dir, log_dir, just_md5, opts_input, input_handler, heartbeat_fn, profile_fn, test_profile, profile_holder, frame_rate
    config = configparser.ConfigParser()
    config.read(config_fn)
    src_dir=config["GLOBAL"]["src_dir"]
    dst_dir=config["GLOBAL"]["dst_dir"]
    convertor = config["GLOBAL"]["convertor"]
    opts_input = config["GLOBAL"]["opts_input"]
    input_handler = config["GLOBAL"]["input_handler"]
    profile_fn = config['GLOBAL']['profile']
    frame_rate = config['GLOBAL']['frame_rate']

    profile_holder = profileHolder(profile_fn)
    if not profile_holder:
        print("can't open profile!!!")
        return -1
    return 0

def test():
    global src_dir, dst_dir, rep_f, convertor, vfile_dir, log_dir, just_md5, opts_input, input_handler, heartbeat_fn, frame_rate
    if read_config() < 0:
        print("read configure file error!!!")
        return
    if src_dir=='' or dst_dir=='':
        print("you must set the source, destination dir")
        return
    #
    log_dir = "%s/logs" % (dst_dir)
    vfile_dir = "%s/files" % (dst_dir)
    rep_fn = "%s/report.csv" % dst_dir
    tmp_dir = "%s/tmp" % dst_dir
    rep_f = open(rep_fn,'w+')
    os.makedirs(log_dir, exist_ok=True)
    os.makedirs(vfile_dir, exist_ok=True)
    os.makedirs(tmp_dir, exist_ok=True)
    heartbeat_fn = '%s/heartbeat' % tmp_dir
    logging.basicConfig(filename="%s/factory_test.log" % dst_dir, level=logging.DEBUG)
    wrtxt="源文件    开始时间    结束时间    转换时长(sec)    成功？\n"
    rep_f.write(wrtxt);
    testDir(src_dir, vfile_dir)
    rep_f.close()
    pass
    
if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    test()
    pass
    

