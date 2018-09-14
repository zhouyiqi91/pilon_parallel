#!usr/bin/env python
#encoding:utf-8
#读入每个split_fa目录下的target_file，以及sorted_bam,生成过滤后的sorted_bam

import sys
import pysam

target_file = sys.argv[1]
sorted_bam = sys.argv[2]
temp_bam = sorted_bam.split("/")[-1] + ".temp"
new_bam = target_file.rstrip(".txt") + "_" + sorted_bam.split("/")[-1]

target_set = set()
with open(target_file,'r') as target:
	for line in target:
		line = line.strip()
		target_set.add(line)

samfile = pysam.AlignmentFile(sorted_bam, "rb" )
pairedreads = pysam.AlignmentFile(temp_bam, "wb", template=samfile)
for target in target_set:
	for read in samfile.fetch(target):
		if read.is_paired:
			pairedreads.write(read)

samfile.close()
pairedreads.close()
pysam.sort("-o", new_bam, temp_bam)
