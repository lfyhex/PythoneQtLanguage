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
read xls all trans and match the all ts to replace
"""

def fill_m2t(ts, mapxls, usetmp):
	srcTSTree = ET.parse(ts)
	root = srcTSTree.getroot()
	for stra in root.iter("message"):
		stdSrc = stra.find("source")
		stdTrans = stra.find("translation")
		if stdSrc.text in mapxls:
			stdTrans.text = mapxls[stdSrc.text]
			stdTrans.attrib = {}
	savetsfile(srcTSTree, ts, usetmp)

def fill_x2t(ts, xlspath, usetmp):
	if not os.path.exists(ts):
		print("ts file not exist")
		return
	if not os.path.exists(xlspath):
		print("excel file not exist")
		return
	mapxls = xlstomap_2(xlspath)
	fill_m2t(ts, mapxls, usetmp)

if __name__=="__main__":
	argvs = sys.argv
	if len(argvs) == 4:
		fill_x2t(argvs[1], argvs[2], argvs[3])
	else:
		print("usage: fill_x2t ts xlspath usetmp")
