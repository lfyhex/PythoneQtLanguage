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
mux ts to ts untranslate
"""
def mux_t_t_untrans(srcts, tarts, usetmp):
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
				if "type" in stdTrans.attrib:
					if stdTrans.attrib["type"] == "unfinished":
						if stdSrc.text in mapTmp:
							stdTrans.text = mapTmp[stdSrc.text]
							stdTrans.attrib = {}

	savetsfile(tSTree, tarts, usetmp)

if __name__=="__main__":
	argvs = sys.argv
	if len(argvs) == 4:
		mux_t_t_untrans(argvs[1], argvs[2], argvs[3])
	else:
		print("usage: mux_t_t_untrans srcts tarts usetmp")
