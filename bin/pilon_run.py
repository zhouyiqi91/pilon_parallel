#!usr/bin/env python
#encoding:utf-8
import sys
import subprocess
import os
import configparser as cp
import glob
import logging
import builtins
from pilon_func import *

#bin_path
builtins.bin_path = os.path.abspath(__file__).strip("pilon_run.py")

#shell prefix
builtins.shell_prefix = "?export PERL5LIB=''\n?source activate pilon\n"

#log
logging.basicConfig(filename='nohup.out',level = logging.INFO,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

#config file
conf_file = sys.argv[1]
config = cp.ConfigParser()
config.read(conf_file)
infile = config["input_file"]
bwa = config["bwa"]
pilon = config["pilon"]

fastq_dir = infile["fastq_dir"]
fasta = infile["fasta"]
name = infile["name"]
run_mode = infile["run_mode"].strip()
#iteration = int(infile["iteration"].strip())
split = int(infile["split"].strip())
genome_size = os.path.getsize(fasta)

bwa_cpu = bwa["cpu"]
bwa_queue = bwa["queue"]
bwa_opts = bwa["opts"].strip()
bwa_mem = int(genome_size/1073741824*3)
if bwa_mem < 5:
	bwa_mem = 5

pilon_cpu = pilon["cpu"]
pilon_mem = pilon["memory"]
pilon_queue = pilon["queue"]
pilon_opts = pilon["opts"].strip()

out_dir = os.getcwd()

run_once(out_dir=out_dir,fastq_dir=fastq_dir,fasta=fasta,name=name,run_mode=run_mode,bwa_cpu=bwa_cpu,bwa_queue=bwa_queue,bwa_opts=bwa_opts,bwa_mem=bwa_mem,pilon_cpu=pilon_cpu,pilon_mem=pilon_mem,pilon_queue=pilon_queue,pilon_opts=pilon_opts,split=split)
if run_mode != "script":
	logging.info("All job done.")

"""
if 0 < iteration < 11:
	pass
else:
	logging.error("iteration should be in [1..10]!")
	exit()
"""

