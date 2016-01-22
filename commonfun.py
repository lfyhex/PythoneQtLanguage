#/bin/python

import os
import xml.dom.minidom as dom
import xml.etree.ElementTree as ET
import csv
import xlwt
import xlrd
import re
import sys
import xml
import subprocess
import types

"""
ts file to map
"""
def savetsfile(xmltree, ts, usetmp):
	destn = ts
	if not usetmp == "0":
		destn += '.tmp'
	xmltree.write(destn, encoding="utf-8")
	lanargs = ["lanupdate.exe", destn]
	subprocess.call(lanargs)

def tstomap(ts):
	mapSTDts = {}
	mapSTD = {}
	stdTree = ET.parse(ts)
	stdRoot = stdTree.getroot()
	for tra in stdRoot.iter("context"):
		stdName = tra.find("name").text
		mapSTD = {}
		for stra in tra.iter("message"):
			stdSrc = stra.find("source").text
			trans = stra.find("translation")
			stdTrans = trans.text
			mapSTD[stdSrc] = stdTrans
		mapSTDts[stdName] = mapSTD
	return mapSTDts

#3 colume
def xlstomap(xlspath):
	mapxtm = {}
	xls = xlrd.open_workbook(xlspath)
	sheets = xls.sheets()
	for sheet in sheets:
		for curRowN in range(0, sheet.nrows):
			# read all of the translated and source text in xlspath file
			na = sheet.cell(curRowN, 0).value
			sr = sheet.cell(curRowN, 1).value
			if type(sr) == type("1"):
				tr = sheet.cell(curRowN, 2).value
				if na not in mapxtm:
					mapxtm[na] = {}
				mapxtm[na][sr] = tr
	return mapxtm

#2 colume
def xlstomap_2(xlspath):
	mapxtm = {}
	xls = xlrd.open_workbook(xlspath)
	sheets = xls.sheets()
	for sheet in sheets:
		for curRowN in range(0, sheet.nrows):
			sr = sheet.cell(curRowN, 0).value
			tr = sheet.cell(curRowN, 1).value
			if type(sr) == type("1"):
				mapxtm[sr] = tr
	return mapxtm

def xlstomap_sheetname_level(xlspath, name):
	mapxtm = {}
	print(xlspath)
	xls = xlrd.open_workbook(xlspath)
	sheets = xls.sheets()
	for sheet in sheets:
		if sheet.name == name:
			for curRowN in range(0, sheet.nrows):
				na = sheet.cell(curRowN, 0).value
				sr = sheet.cell(curRowN, 1).value
				tr = sheet.cell(curRowN, 2).value
				if type(sr) == type("1") and type(tr) == type("1") and type(na) == type("1"):
					if na not in mapxtm:
						mapxtm[na] = {}
					mapxtm[na][sr] = tr
	return mapxtm

def createTSItem(node, src, trans):
	treebuild = xml.etree.ElementTree.TreeBuilder()
	#source
	treebuild.start("source", {})
	treebuild.data(src)
	srcTag = treebuild.end("source")

	#translation
	treebuild2 = xml.etree.ElementTree.TreeBuilder()
	treebuild2.start("translation", {})
	treebuild2.data(trans)
	transTag = treebuild2.end("translation")

	#message
	treebuild3 = xml.etree.ElementTree.TreeBuilder()
	treebuild3.start("message", {})
	msgTag = treebuild3.end("message")

	msgTag.append(srcTag)
	msgTag.append(transTag)
	node.append(msgTag)

def createTsItemName(node, na):
	treebuild = xml.etree.ElementTree.TreeBuilder()
	#context
	treebuild.start("context", {})
	conTag = treebuild.end("context")
	#name
	treebuild2 = xml.etree.ElementTree.TreeBuilder()
	treebuild2.start("name", {})
	treebuild2.data(na)
	naTag = treebuild2.end("name")
	conTag.append(naTag)
	node.append(conTag)
	return conTag