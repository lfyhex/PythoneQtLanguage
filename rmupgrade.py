
import os
import sys
from datetime import datetime
from datetime import timedelta
import time

"""
list upgrade files and dirs
"""
def list_upgrade(fpath, lst):
    if not os.path.exists(fpath):
        print(fpath + " is not exits!!!")
        return

    absfpath = os.path.abspath(fpath)
    cur_date = datetime.now()
    for f in os.listdir(absfpath):
        newpath = absfpath + '/' + f
        if '_upgrade' in f:
            #one month ago
            stat_info = os.stat(newpath)
            stat_date = datetime.fromtimestamp(stat_info.st_ctime)
            t_date = stat_date + timedelta(60)
            if (cur_date > t_date):
                print('----append path----' + newpath)
                lst.append(newpath)
            else:
                print('*********upgrade blow one moth*********')
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
            inputFile = open(argvs[2], 'r');
            for l in inputFile:
                rmfilepath = l.strip()
                if os.path.exists(rmfilepath):
                    print('remove ' + rmfilepath)
                    os.system('rm -rf ' + '"' + rmfilepath + '"')
        elif argvs[1] == 'list':
            lstret = [];
            list_upgrade(argvs[2], lstret);
            fresult = open('list_result.txt', 'w');
            print('----start print result----')
            for i in lstret:
                print(i)
                fresult.write(i)
                fresult.write("\n")
            print('----end----')
    else:
        print("usage: list | rm file path")
