#!usr/bin/env python
#encoding:utf-8
#读入split_fa.fasta,在split_fa目录下生成split_fa.txt,记录所有scaf名称

import sys
import os

split_fa = sys.argv[1]
target_file = open(split_fa+"/"+split_fa+".txt",'w')
with open(split_fa+".fasta",'r') as split_fa_fasta:
	for line in split_fa_fasta:
		line = line.strip()
		if line[0] == ">":
			scaf_name = line.lstrip(">").split(" ")[0]
			target_file.write(scaf_name+"\n")	

target_file.close()
os.system("mv "+split_fa+".fasta "+split_fa+"/")
