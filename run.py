#/bin/python

import os
import re
import sys
import subprocess
import configparser

g_usetmp = 1

def run():
	config_fn = "config.ini"
	config = configparser.ConfigParser()
	fname = config.read(config_fn)
	if len(fname) == 0:
		print("config file not exist")
		return
	act = config["default"]["action"]
	pypath = config["default"]["pypath"]
	g_usetmp = config["default"]["usetmpts"]

	if not os.path.exists(pypath):
		print("python path not exist")
		return
	demux_args = [pypath, "demux.py"] + list(config["demux"].values())
	mux_t_t_args = [pypath, "mux_t_t.py"] + list(config["mux_t_t"].values()) + [g_usetmp]
	mux_t_x_args = [pypath, "mux_t_x.py"] + list(config["mux_t_x"].values()) + [g_usetmp]
	fill_x2t_args = [pypath, "fill_x2t.py"] + list(config["fill_x2t"].values()) + [g_usetmp]
	extract_args = [pypath, "extract.py"] + list(config["extract"].values())
	extract_untranslate_args = [pypath, "extract_untranslate.py"] + list(config["extract_untranslate"].values())
	mux_t_t_untrans_args = [pypath, "mux_t_t_untrans.py"] + list(config["mux_t_t_untrans"].values()) + [g_usetmp]
	im_export_args = [pypath, "im_export.py"] + list(config["im_export"].values()) + [g_usetmp]

	if act == "demux":
		subprocess.call(demux_args)
	elif act == "mux_t_t":
		subprocess.call(mux_t_t_args)
	elif act == "mux_t_x":
		subprocess.call(mux_t_x_args)
	elif act == "extract":
		subprocess.call(extract_args)
	elif act == "extract_untranslate":
		subprocess.call(extract_untranslate_args)
	elif act == "fill_x2t":
		subprocess.call(fill_x2t_args)
	elif act == "mux_t_t_untrans":
		subprocess.call(mux_t_t_untrans_args)
	elif act == "im_export":
		subprocess.call(im_export_args)

if __name__=="__main__":
	run()

