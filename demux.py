#/bin/python

import os
import xml.dom.minidom as dom
import xml.etree.ElementTree as ET
import csv
import xlwt
import xlrd
import re
import sys
from commonfun import tstomap, xlstomap, createTSItem, createTsItemName

"""
compare std ts file with target ts file and generate diff xls file
"""
def demux(stdts, tgts, xlspath, xlsname):
	if not os.path.exists(stdts):
		return
	if not os.path.exists(tgts):
		return
	mapXls = {}
	mapSTDts = tstomap(stdts)
	mapTts = tstomap(tgts)
	for na in mapTts:
		if na in mapSTDts:
			mapS = mapSTDts[na]
			mapT = mapTts[na]
			mapTemp = {}
			for s in mapT:
				if s not in mapS:
					mapTemp[s] = mapT[s]
			if len(mapTemp) > 0:
				mapXls[na] = mapTemp
		else:
			mapXls[na] = mapTts[na]
	xlswriter = xlwt.Workbook("unicode")
	sheet = xlswriter.add_sheet(xlsname)
	row = 0
	for na in mapXls:
		mapTmp = mapXls[na]
		for src in mapTmp:
			sheet.write(row, 0 ,na)
			sheet.write(row, 1, src)
			sheet.write(row, 2, mapTmp[src])
			row += 1
	destFn = xlspath + "/" + xlsname + ".xls"
	xlswriter.save(destFn)

if __name__=="__main__":
	argvs = sys.argv
	if len(argvs) == 5:
		demux(argvs[1], argvs[2], argvs[3], argvs[4])
	else:
		print("usage: demum stdts targetts xlsdir xlsname")
