"""
remove files
"""

import os
import sys
import re

REMOVE_CONTAINS = ['_beta', '_test']

def exact_version(strfile):
    '''
    get version from string
    '''
    mag = re.search(r'[\d]+\.[\d]+\.[\d]+', strfile)
    if mag:
        return mag.group(0)
    return ''

def can_remove(fileordir):
    '''
    judge the file or folder can removed
    '''
    is_remove = False
    ver = exact_version(fileordir)
    if len(ver):
        first_v = ver.split('.')[0]
        nver = int(first_v)
        if nver == 0 or nver >= 99:
            is_remove = True
    if not is_remove:
        for spec in REMOVE_CONTAINS:
            if spec in fileordir:
                is_remove = True
                break
    return is_remove


def rm_fit_files(tar):
    '''
    remove imp
    '''
    lstfiles = os.listdir(tar)
    for onef in lstfiles:
        newpath = tar + '/' + onef
        if can_remove(onef):
            os.system('rm -rf ' + '"' + newpath + '"')
            print(newpath)
        elif onef.endswith('.app'):
            print('not into app contents')
        elif os.path.isdir(newpath):
            rm_fit_files(newpath)

if __name__ == "__main__":
    '''
    usage: py targepath
    '''
    if len(sys.argv) == 2:
        TATGET = sys.argv[1]
        if os.path.exists(TATGET):
            rm_fit_files(TATGET)
        else:
            print("target path is not exist")
    else:
        print("usage: py file path")
