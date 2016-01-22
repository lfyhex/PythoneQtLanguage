#/bin/python

import os
import xml.dom.minidom as dom
import xml.etree.ElementTree as ET
import csv
import xlwt
import xlrd
import re
import sys
from commonfun import tstomap
"""
extract un translate message to xls
"""
def extract_untranslate(ts, xlsdir, xlsname):
	if not os.path.exists(ts):
		print("ts is not exits!!!")
		return
	if not os.path.exists(xlsdir):
		print("xlsdir is not exist!!!")
		return
	mapTs = tstomap(ts)
	mapExt = {}
	for na in mapTs:
		for src in mapTs[na]:
			if mapTs[na][src] is None:
				if na not in mapExt:
					mapExt[na] = {}
				mapExt[na][src] = ""

	if len(mapExt) > 0:
		xlswriter = xlwt.Workbook("utf-8")
		sheet = xlswriter.add_sheet(xlsname)
		row = 0
		for na in mapExt:
			for src in mapExt[na]:
				sheet.write(row, 0 ,na)
				sheet.write(row, 1, src)
				row += 1
		destFn = xlsdir + "/" + xlsname + ".xls"
		xlswriter.save(destFn)

if __name__=="__main__":
	argvs = sys.argv
	if len(argvs) == 4:
		extract_untranslate(argvs[1], argvs[2], argvs[3])
	else:
		print("usage: extract_untranslate ts xlsdir xlsname")
