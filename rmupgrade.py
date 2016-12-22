
import os
import sys
from datetime import datetime
from datetime import timedelta
import time
import re

"""
list upgrade files and dirs
"""

def exactVersion(strFile):
    ma=re.search(r'[\d]+\.[\d]+\.[\d]+', strFile)
    return ma.group(0)

def max_version(v1, v2):
    lstV1 = v1.split(".")
    lstV2 = v2.split(".")
    ret = 0
    for d in range(len(lstV1)):
        intV1 = int(lstV1[d])
        intV2 = int(lstV2[d])
        if intV1 > intV2:
            ret = 1
            break
        elif intV1 < intV2:
            ret = -1
            break
    return ret

def classification_max_versions(lst):
    odd_versions = set([])
    even_versions = set([])
    for f in lst:
        if '_upgrade' in f:
            strV = exactVersion(f)
            last_char = strV[-1]
            n = int(last_char)
            if n % 2 == 0:
                even_versions.add(strV)
            else:
                odd_versions.add(strV)
    odd_max = "0.0.0"
    even_max = "0.0.0"
    for s in odd_versions:
        cmp_res = max_version(s, odd_max)
        if (cmp_res == 1):
            odd_max = s

    for s in even_versions:
        cmp_res = max_version(s, even_max)
        if (cmp_res == 1):
            even_max = s

    res = []
    if (len(odd_max)):
        res.append(odd_max)
    if (len(even_max)):
        res.append(even_max)

    return res

def list_upgrade(fpath, lst):
    if not os.path.exists(fpath):
        print(fpath + " is not exits!!!")
        return

    absfpath = os.path.abspath(fpath)
    cur_date = datetime.now()
    lstfiles = os.listdir(absfpath)
    
    max_versions = classification_max_versions(lstfiles)

    for f in lstfiles:
        newpath = absfpath + '/' + f
        if '_upgrade' in f:
            strV = exactVersion(f)
            if strV in max_versions:
                continue
            #two month ago
            stat_info = os.stat(newpath)
            stat_date = datetime.fromtimestamp(stat_info.st_ctime)
            t_date = stat_date + timedelta(60)
            if (cur_date > t_date):
                print('----append path----' + newpath)
                lst.append(newpath)
            else:
                print('*********upgrade blow two moth*********')
                print(f)
        else:
            if f.endswith('.app'):
                print('not into app contents')
            elif os.path.isdir(newpath):
                print('go to sub dir' + newpath)
                list_upgrade(newpath, lst)


def rm_files(lstPath):
    for ipath in lstPath:
        if os.path.exists(ipaht):
            os.system('rm -rf ' + ipaht)

if __name__=="__main__":
    argvs = sys.argv
    if len(argvs) == 3:
        if argvs[1] == 'rm':
            inputFile = open(argvs[2], 'r')
            for l in inputFile:
                rmfilepath = l.strip()
                if os.path.exists(rmfilepath):
                    print('remove ' + rmfilepath)
                    os.system('rm -rf ' + '"' + rmfilepath + '"')
        elif argvs[1] == 'list':
            lstret = []
            list_upgrade(argvs[2], lstret)
            fresult = open('list_result.txt', 'w')
            print('----start print result----')
            for i in lstret:
                print(i)
                fresult.write(i)
                fresult.write("\n")
            fresult.flush()
            print('----end----')
    else:
        print("usage: list | rm file path")
