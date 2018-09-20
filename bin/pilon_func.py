#!usr/bin/env python
#encoding:utf-8
import subprocess
import os
import logging
import glob
import math

def write_shell(shell_name,shell_prefix,shell_cont):
	with open(shell_name,'w') as shell:
		shell.write(shell_prefix)
		shell.write(shell_cont)

def shell_submit(bin_path,cut,cpu,mem,queue,opts,shell_path,shell_name):
	if not os.path.exists(shell_path+shell_name+".done"):
		cmd = "python "+bin_path+"sgearray.py -l vf="+str(mem)+",p="+str(cpu)+" -c "+str(cut)+" -q "+queue+" "+opts+" "+shell_path+shell_name+"\n"
		logging.info(cmd)
		ret = subprocess.call(cmd,shell=True)
		if ret == 0:
			logging.info(shell_path+shell_name+" done.")
			os.system("touch "+shell_path+shell_name+".done")
		else:
			logging.error(shell_path+shell_name+" failed!")
			exit()
	else:
		logging.info(shell_path+shell_name+" already finished!")

def run_once(out_dir,fastq_dir,fasta,name,run_mode,bwa_cpu,bwa_queue,bwa_opts,bwa_mem,pilon_cpu,pilon_mem,pilon_queue,pilon_opts,split):
	new_fasta = out_dir + "/pilon_output/"+name+".fasta"
	if run_mode in ["all","script"]:
		#bwa index
		os.chdir(out_dir)
		os.system("mkdir pilon_output")
		os.chdir("pilon_output")
		shell_name = "index.sh"
		shell_cont = "cp "+fasta+" "+name+".fasta\n"
		shell_cont += "bwa index " + name + ".fasta\n"
		write_shell(shell_name,shell_prefix,shell_cont)

		#bwa mem
		shell_name = "align.sh"
		shell_cont = ""
		read1s = glob.glob(fastq_dir+"/*_1*.fq") + glob.glob(fastq_dir+"/*_1*.fq.gz") 
		if not read1s:
			logging.error("No *.fq or *.fq.gz in fastq_dir!")
			exit()
#+ glob.glob(fastq_dir+"/*_1*.fastq") + glob.glob(fastq_dir+"/*_1*.fastq.gz")
		#sorted_bams = []
		bams = []
		for read1 in read1s:
			prefix = read1.split("/")[-1].split("_1")[0]
			read2 = (glob.glob(fastq_dir+"/"+prefix+"_2*.fq")+glob.glob(fastq_dir+"/"+prefix+"_2*.fq.gz"))[0]
			shell_cont += ("""bwa mem -t """+str(bwa_cpu)+""" """+new_fasta+""" """+read1+""" """+read2+""" |samtools view -Sb - >"""+prefix+""".bam\n""")
			#shell_cont += ("""samtools sort """+prefix+""".bam """+prefix+"""_sort\n""")
			#shell_cont += ("""samtools index """+prefix+"""_sort.bam \n""")
			#sorted_bams.append(out_dir+"/pilon_output/"+prefix+"_sort.bam")
			bams.append(out_dir+"/pilon_output/"+prefix+".bam")
		write_shell(shell_name,shell_prefix,shell_cont)

		#split_fa
		shell_name = "split_fa.sh"
		shell_cont = "pyfasta split -n "+str(split) + " " +new_fasta +"\n"
		write_shell(shell_name,shell_prefix,shell_cont)
		split_fas = []
		fill_number = int(math.log10(split)) + 1
		for index in range(split):
			new_index = str(index).zfill(fill_number)
			split_fa = name+"."+new_index
			split_fas.append(split_fa)
			os.system("mkdir "+split_fa)
		
		#create target file
		shell_name = "create_target.sh"
		shell_cont = ""
		for split_fa in split_fas:
			shell_cont += "python " + bin_path + "create_target.py "+ split_fa +"\n"
		write_shell(shell_name,shell_prefix,shell_cont)
		
		#split_bam
		frags_line = {}
		shell_name = "split_bam.sh"
		shell_cont = ""
		for split_fa in split_fas:
			frags_line[split_fa] = ""
			for bam in bams:
				target_file = split_fa + ".txt"
				shell_cont += "cd " + split_fa + " && python " + bin_path + "split_bam.py " + target_file + " " + bam +"\n"
				bam_name= bam.split("/")[-1]
				new_bam = split_fa + "_" + bam_name
				frags_line[split_fa] += " --frags " + new_bam
				shell_cont += "samtools index " + new_bam +"\n"
		write_shell(shell_name,shell_prefix,shell_cont)


		#pilon
		shell_name = "pilon.sh"
		shell_cont = ""
		for split_fa in split_fas:
			shell_cont += "cd "+split_fa + " && pilon -Xmx"+pilon_mem+" --diploid --changes --threads "+pilon_cpu+" --output "+split_fa+ "_pilon " + " --genome " + new_fasta + " "+frags_line[split_fa] + " --targets `cat " + split_fa +".txt`\n"
		write_shell(shell_name,shell_prefix,shell_cont)

		logging.info("Scripts generated.")

		#submit
	if run_mode in ["all","submit"]:
		os.chdir(out_dir)
		os.chdir("pilon_output")
		#index
		cut = 2
		shell_name = "index.sh"
		shell_submit(bin_path,cut,1,bwa_mem,bwa_queue,bwa_opts,"",shell_name)

		#align
		cut = 1
		shell_name = "align.sh"
		shell_submit(bin_path,cut,bwa_cpu,bwa_mem,bwa_queue,bwa_opts,"",shell_name)

		#split_fa
		cut = 1
		shell_name = "split_fa.sh"
		shell_submit(bin_path,cut,1,bwa_mem,bwa_queue,bwa_opts,"",shell_name)

		#create target file
		cut = 1
		shell_name = "create_target.sh"
		shell_submit(bin_path,cut,1,bwa_mem,bwa_queue,bwa_opts,"",shell_name)

		#split_bam
		cut = 2
		shell_name = "split_bam.sh"
		shell_submit(bin_path,cut,1,"2G",bwa_queue,bwa_opts,"",shell_name)

		#pilon
		cut = 1
		shell_name = "pilon.sh"
		shell_submit(bin_path,cut,pilon_cpu,pilon_mem,pilon_queue,pilon_opts,"",shell_name)

		#merge
		if not os.path.exists(name+"_pilon.fasta"):
			os.system("cat "+name+".*/"+name+".*_pilon.fasta >"+name+"_pilon.fasta")
		if not os.path.exists(name+"_pilon.changes"):
			os.system("cat "+name+".*/"+name+".*_pilon.changes >"+name+"_pilon.changes")
		

			
