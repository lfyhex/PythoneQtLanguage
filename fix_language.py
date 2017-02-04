
import sys
import os
import xml.etree.ElementTree as ET
import re
import configparser
from colorama import init, Back

init()

'''
this file is used to fix code strings
'''

def valid_cstring_end(cstring, index):
    '''
    judge c string end
    '''
    trans_cnt = 0
    for idx in range(index - 1, -1, -1):
        if idx >= 0 and cstring[idx] == '\\':
            trans_cnt += 1
        else:
            break
    if trans_cnt % 2 == 0:
        return True
    return False

def string_to_cstring(pystr, spacepad=16):
    '''
    change py string to cstring
    '''
    retstring = ''
    for onechar in pystr:
        if onechar in ['\\', '"']:
            retstring += '\\'
        elif onechar == '\n':
            retstring += '\\n'
            continue
        retstring += onechar
    newstring = ''
    cnt = len(retstring)
    if spacepad and cnt + spacepad > 140:
        singlelines = 140 - spacepad - 2
        i = 0
        readedindx = 0
        while cnt > i * singlelines:
            end = (i+1)*singlelines
            if end >= cnt:
                end = cnt - 1
            while retstring[end] not in [' ', ',', ';', '.', '?'] and end < cnt:
                end += 1
            if end < cnt and end + 5 < cnt:
                construcstr = retstring[readedindx:end] + '"\n' + ' ' * spacepad + '"'
                readedindx = end
                newstring += construcstr
            else:
                newstring += retstring[readedindx:-1]
            i += 1
        retstring = newstring
    return retstring

def cstring_to_string(cstring):
    '''
    change c string to normal string
    '''
    realcstring = ''
    orgstr = cstring
    for mag in re.finditer('\"\n[ ]+\"', orgstr):
        matstr = mag.group(0)
        orgstr = orgstr.replace(matstr, '')

    i = 0
    preidx = 0
    cnt = len(orgstr)
    while i < cnt:
        if orgstr[i] == '\\':
            add2 = False
            if i + 1 < cnt:
                if orgstr[i + 1] == '\\':
                    i += 1
                elif orgstr[i + 1] == 'n':
                    add2 = True
                    i += 2
            realcstring += orgstr[preidx:i]
            if add2:
                i -= 1
            preidx = i
        else:
            realcstring += orgstr[i]
            preidx = i + 1

        i += 1
    realcstring = realcstring.replace('\\n', '\n')
    return realcstring

def parse_code_file(str_contents):
    '''
    find all code file string
    '''
    i = 0
    preindex = -1
    mapret = []
    cnt = len(str_contents)
    while i < cnt:
        if str_contents[i] == '"' and valid_cstring_end(str_contents, i):
            if preindex == -1:
                preindex = i
            else:
                contloop = False
                for j in range(i + 1, cnt):
                    if str_contents[j] == '"' and valid_cstring_end(str_contents, j):
                        if j - i > 1:
                            allblank = True
                            for k in range(i+1, j):
                                if str_contents[k] not in ['\n', ' ']:
                                    allblank = False
                                    break
                            if allblank:
                                contloop = True
                                i = j
                        else:
                            contloop = True
                        break
                if not contloop:
                    str_srcrange = str_contents[preindex + 1:i]
                    if len(str_srcrange):
                        #[ src_txt, left, right, space need pad ]
                        spacepad = 0
                        for idx in range(preindex, -1, -1):
                            if str_contents[idx] == ' ':
                                spacepad += 1
                            elif str_contents[idx] == '\n':
                                break
                            else:
                                spacepad = 0
                        sigi = [cstring_to_string(str_srcrange), preindex + 1, i, spacepad]
                        mapret.append(sigi)
                        preindex = -1
        i += 1
    return mapret

def replace_one_file(tsi, codefile):
    '''
    real replace
    '''
    codef = open(codefile, mode='r')
    str_contents = codef.read()
    codef.close()
    str_texts = parse_code_file(str_contents)
    new_infos = []
    #filt
    i = 0
    srctsikeys = tsi.keys()
    while i < len(str_texts):
        if str_texts[i][0] not in srctsikeys:
            del str_texts[i]
            i -= 1
        i += 1
    #set replaced string
    replaced_list = []
    for sigi in str_texts:
        for src in tsi:
            if sigi[0] == src:
                infos = [sigi[1], sigi[2], tsi[src], sigi[3]]
                new_infos.append(infos)
                replaced_list.append(src)
                break
    for src in tsi:
        if src not in replaced_list:
            print(Back.RED + 'Warning str:%s not replaced' % src + Back.RESET)
    #replace
    final_contents = ''
    left_index = 0
    for oneinfo in new_infos:
        leftidx = oneinfo[0]
        rightidx = oneinfo[1]
        newstr = oneinfo[2]
        #fixme
        final_contents += str_contents[left_index:leftidx]
        final_contents += string_to_cstring(newstr, oneinfo[3])
        left_index = rightidx
    if left_index < len(str_contents):
        final_contents += str_contents[left_index:]
    #save file
    codef = open(codefile.lower(), mode='w')
    codef.write(final_contents)
    codef.close()

def replace_code(tsinfo, codefolder):
    '''
    replace code string
    '''
    for tsname in tsinfo:
        #find code file
        code_file = codefolder + '/' + tsname + '.cpp'
        if not os.path.exists(code_file):
            code_file = codefolder + '/' + tsname + '.h'
            if not os.path.exists(code_file):
                code_file = ''
        if len(code_file):
            onfileinfo = tsinfo[tsname]
            replace_one_file(onfileinfo, code_file)
        else:
            print("code file not find")

def tstomap(tsf):
    '''
    ts file to map { Name { source transe } }
    '''
    mapstdts = {}
    stdtree = ET.parse(tsf)
    stdroot = stdtree.getroot()
    for tra in stdroot.iter("context"):
        stdname = tra.find("name").text
        mst = {}
        for stra in tra.iter("message"):
            stdsrc = stra.find("source").text
            trans = stra.find("translation")
            if len(trans.attrib) and trans.attrib['type'] == 'unfinished' and len(trans.text):
                if stdsrc != trans.text:
                    mst[stdsrc] = trans.text
        if len(mst):
            mapstdts[stdname] = mst
    return mapstdts

def parse_ts_files(tsfolder):
    '''
    return { filename { moudle string } }
    '''
    lstfiles = os.listdir(tsfolder)
    map_files_info = {}
    for fts in lstfiles:
        fabsp = tsfolder + '/' + fts
        map_files_info[fts] = tstomap(fabsp)
    return map_files_info

def find_match_code_foder(tsname, codefolder):
    '''
    find ts file ==> code folder
    eg:
    FfVideoEditor_en.ts ==> Controls/FfVideoEditor
    '''
    lstfiles = os.listdir(codefolder)
    for validf in lstfiles:
        newpath = codefolder + '/' + validf
        if os.path.isdir(newpath):
            if validf == tsname:
                return newpath
            elif validf not in ['.svn', 'Components', 'build', 'language', 'skin']:
                find_match_code_foder(tsname, newpath)
    return ''

def change(tsfolder, codefolder):
    '''
    imp
    '''
    if not os.path.exists(tsfolder) or not os.path.exists(codefolder):
        print('ts folder or code folder not exist')
        return
    ts_infos = parse_ts_files(tsfolder)
    for tsi in ts_infos:
        #first find code location
        if tsi.endswith('_en.ts'):
            tsname = tsi.replace('_en.ts', '')
            code_ts_folder = find_match_code_foder(tsname, codefolder)
            single_ts_info = ts_infos[tsi]
            replace_code(single_ts_info, code_ts_folder)
        else:
            print("ts file name is not valid " + tsi)

def run():
    '''
    usage: --ts_src path --code_src path
    '''
    if len(sys.argv) == 5:
        tsf = sys.argv[2]
        codef = sys.argv[4]
        change(tsf, codef)
    else:
        #read config file
        config_fn = 'fix_language.ini'
        if os.path.exists(config_fn):
            print('read configure ini file')
            cfg = configparser.ConfigParser()
            cfg.read(config_fn)
            tsf = cfg['GLOBAL']['tsdir']
            codef = cfg['GLOBAL']['codedir']
            change(tsf, codef)

if __name__ == '__main__':
    run()
