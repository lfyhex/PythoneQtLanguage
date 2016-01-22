#/bin/python

import os
import xml.dom.minidom as dom
import xml.etree.ElementTree as ET
import csv
import xlwt
import xlrd
import re
import sys
from commonfun import tstomap, xlstomap_2, createTSItem, createTsItemName, savetsfile
"""
change the ts src
"""

def cg(ts, mapxls, usetmp):
	srcTSTree = ET.parse(ts)
	root = srcTSTree.getroot()
	for stra in root.iter("message"):
		stdSrc = stra.find("source")
		if stdSrc.text in mapxls:
			stdSrc.text = mapxls[stdSrc.text]
	savetsfile(srcTSTree, ts, usetmp)

def cg_ts_srctxt(ts, xlspath, usetmp):
	if not os.path.exists(ts):
		print("ts file not exist")
		return
	if not os.path.exists(xlspath):
		print("excel file not exist")
		return
	mapxls = xlstomap_2(xlspath)
	cg(ts, mapxls, usetmp)

if __name__=="__main__":
	argvs = sys.argv
	if len(argvs) == 4:
		cg_ts_srctxt(argvs[1], argvs[2], argvs[3])
	else:
		print("usage: cg_ts_srctxt ts xlspath usetmp")
