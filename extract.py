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
extract ts file special value to xls
"""
def extract(ts, name, xlsdir, xlsname):
	if not os.path.exists(ts):
		print("ts is not exits!!!")
		return
	if not os.path.exists(xlsdir):
		print("xlsdir is not exist!!!")
		return
	mapTs = tstomap(ts)
	if len(name) > 0 and name in mapTs:
		xlswriter = xlwt.Workbook("utf-8")
		sheet = xlswriter.add_sheet(xlsname)
		row = 0
		mapTmp = mapTs[name]
		for src in mapTmp:
			sheet.write(row, 0 ,name)
			sheet.write(row, 1, src)
			sheet.write(row, 2, mapTmp[src])
			row += 1
		destFn = xlsdir + "/" + xlsname + ".xls"
		xlswriter.save(destFn)

if __name__=="__main__":
	argvs = sys.argv
	if len(argvs) == 5:
		extract(argvs[1], argvs[2], argvs[3], argvs[4])
	else:
		print("usage: extract ts name xlsdir xlsname")
