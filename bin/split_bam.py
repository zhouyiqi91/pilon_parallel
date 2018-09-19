#!usr/bin/env python
#encoding:utf-8
#读入每个split_fa目录下的target_file，以及sorted_bam,生成过滤后的sorted_bam

import sys
import pysam

target_file = sys.argv[1]
bam = sys.argv[2]
temp_bam = bam.split("/")[-1] + ".temp"
new_bam = target_file.rstrip(".txt") + "_" + bam.split("/")[-1]

target_set = set()
with open(target_file,'r') as target:
	for line in target:
		line = line.strip()
		attr = line.split(",")
		for item in attr:
			target_set.add(item)

samfile = pysam.AlignmentFile(bam, "rb" )
pairedreads = pysam.AlignmentFile(temp_bam, "wb", template=samfile)
for read in samfile.fetch(until_eof=True):
	if read.is_read1:
		read1 = read
	else:
		read2 = read
		read1_ref = samfile.get_reference_name(read1.reference_id)
		read2_ref = samfile.get_reference_name(read2.reference_id)
		if read1_ref in target_set or read2_ref in target_set:
			pairedreads.write(read1)
			pairedreads.write(read2)

samfile.close()
pairedreads.close()
pysam.sort("-o", new_bam, temp_bam)
