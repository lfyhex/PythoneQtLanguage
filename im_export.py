#/bin/python

import os
import xml.dom.minidom as dom
import xml.etree.ElementTree as ET
import csv
import xlwt
import xlrd
import re
import sys
import configparser
from commonfun import tstomap, xlstomap, xlstomap_sheetname_level
from mux_t_x import mux_t_m

def import_ts(tsdirpath, lan, xlsdir, xlsname, usetemp):
	xlsfilepath = xlsdir + "/" + xlsname + "_" + lan + ".xls"
	if not os.path.exists(xlsfilepath):
		print("xlsfilepath not ejxist")
		return
	for f in os.listdir(tsdirpath):
		tspath = tsdirpath + "/" + f
		lst = os.path.basename(f).split(".")
		tsext = lst[-1]
		if tsext == "ts":
			tsname = lst[0]
			tsname = tsname[0:len(tsname) - len(lan) - 1]
			xlsmap = xlstomap_sheetname_level(xlsfilepath, tsname)
			mux_t_m(tspath, xlsmap, usetemp)

def import_alllanguage(langpath, xlsdir, xlsname, usetemp):
	for f in os.listdir(langpath):
		tsdirpath = langpath + "/" + f
		if f == "en":
			continue
		import_ts(tsdirpath, f, xlsdir, xlsname, usetemp)

def export(tspath, lan, xlsdir, xlsname):
	mapAll = {}
	for f in os.listdir(tspath):
		fname = os.path.basename(f).split(".")[0]
		fname = fname[0:len(fname) - len(lan) - 1]
		fpath = tspath + "/" + f
		mapAll[fname] = tstomap(fpath)
	xlswriter = xlwt.Workbook("unicode")
	for stname in mapAll:
		#sheet name
		sheet = xlswriter.add_sheet(stname)
		row=0
		for ty in mapAll[stname]:
			for na in mapAll[stname][ty]:
				sheet.write(row, 0, ty)
				sheet.write(row, 1, na)
				sheet.write(row, 2, mapAll[stname][ty][na])
				row += 1
	destFn = xlsdir + "/" + xlsname + "_" + lan + ".xls"
	xlswriter.save(destFn)

def export_alllanguage(langpath, xlsdir, xlsname):
	for f in os.listdir(langpath):
		tspath = langpath + "/" + f
		export(tspath, f, xlsdir, xlsname)

def main():
	config_fn = "config.ini"
	config = configparser.ConfigParser()
	fname = config.read(config_fn)
	if len(fname) == 0:
		print("config file not exist")
		return
	action = config["im_export"]["action"]
	langpath = config["im_export"]["langpath"]
	xlsdir = config["im_export"]["xlsdir"]
	xlsname = config["im_export"]["xlsname"]
	usetmp = config["default"]["usetmpts"]

	if not os.path.exists(langpath):
		print(langpath)
		print("langpath not exist")
		return
	if not os.path.exists(xlsdir):
		print("xlsdir not exist")
		return

	if action == "export":
		export_alllanguage(langpath, xlsdir, xlsname)
	elif action == "import":
		import_alllanguage(langpath, xlsdir, xlsname, usetmp)
	else:
		print("action is not valid")

if __name__=="__main__":
	main()
