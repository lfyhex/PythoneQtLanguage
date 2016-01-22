#/bin/python

import os
import xml.dom.minidom as dom
import xml.etree.ElementTree as ET
import csv
import xlwt
import xlrd
import re
import sys
from commonfun import tstomap, xlstomap, createTSItem, createTsItemName, savetsfile
"""
mux ts and xls to ts.tmp
you need use Qt linguist open the ts.tmp and save to format the ts file
"""

def mux_t_m(ts, mapxls, usetmp):
	srcTSTree = ET.parse(ts)
	root = srcTSTree.getroot()
	for tra in root.iter("context"):
		name = tra.find("name").text
		if name in mapxls:
			mapTmp = mapxls[name]
			for stra in tra.iter("message"):
				stdSrc = stra.find("source")
				stdTrans = stra.find("translation")
				if stdSrc.text in mapTmp:
					stdTrans.text = mapTmp[stdSrc.text]
					stdTrans.attrib = {}
					del mapTmp[stdSrc.text]
			for nitem in mapTmp:
				createTSItem(tra, nitem, mapTmp[nitem])
			del mapxls[name]
	for n in mapxls:
		if type(n) != type("1"):
			continue
		contag = createTsItemName(root, n)
		for nitem in mapxls[n]:
			createTSItem(contag, nitem, mapxls[n][nitem])
	savetsfile(srcTSTree, ts, usetmp)

def mux_t_x(ts, xlspath, usetmp):
	if not os.path.exists(ts):
		print("ts file not exist")
		return
	if not os.path.exists(xlspath):
		print("excel file not exist")
		return
	mapxls = xlstomap(xlspath)
	mux_t_m(ts, mapxls, usetmp)

if __name__=="__main__":
	argvs = sys.argv
	if len(argvs) == 4:
		mux_t_x(argvs[1], argvs[2], argvs[3])
	else:
		print("usage: mux_t_x ts xlspath usetmp")
