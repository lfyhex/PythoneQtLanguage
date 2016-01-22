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
mux ts and ts to ts.tmp
you need use Qt linguist open the ts.tmp and save to format the ts file
"""
def mux_t_t(srcts, tarts, usetmp):
	if not os.path.exists(srcts):
		print("src ts file not exist!!!")
		return
	if not os.path.exists(tarts):
		print("target ts file not exist!!!")
		return
	mapSrc = tstomap(srcts)
	tSTree = ET.parse(tarts)
	root = tSTree.getroot()
	for tra in root.iter("context"):
		name = tra.find("name").text
		if name in mapSrc:
			mapTmp = mapSrc[name]
			for stra in tra.iter("message"):
				stdSrc = stra.find("source")
				stdTrans = stra.find("translation")
				if stdSrc.text in mapTmp:
					stdTrans.text = mapTmp[stdSrc.text]
					stdTrans.attrib = {}
					del mapTmp[stdSrc.text]
			for nitem in mapTmp:
				createTSItem(tra, nitem, mapTmp[nitem])
			del mapSrc[name]
	for n in mapSrc:
		contag = createTsItemName(root, n)
		for nitem in mapSrc[n]:
			createTSItem(contag, nitem, mapSrc[n][nitem])
	savetsfile(tSTree, tarts, usetmp)

if __name__=="__main__":
	argvs = sys.argv
	if len(argvs) == 4:
		mux_t_t(argvs[1], argvs[2], argvs[3])
	else:
		print("usage: mux_t_t srcts tarts usetmp")
