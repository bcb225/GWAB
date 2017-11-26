import sys
import csv
import re
import subprocess


range = sys.argv[4]
genes = dict()
gene_file = open(sys.argv[2],'rb')
reader = csv.reader(gene_file)
count = 0
for row in reader:
	#row[1] = chr_num
	#row[3] = start & row[4] = end
	#row[11] = align_id
	p = re.compile('(\d+|x|y|X|Y|M)')
	chr_detect = p.findall(row[0])
	temp = [row[1],row[2],row[3]]
	if chr_detect[0] in genes:
		genes[chr_detect[0]].append(temp)
	else:
		print row[0]
		#print chr_detect[0]
		genes[chr_detect[0]] = []
		genes[chr_detect[0]].append(temp)
gene_file.close()

gwas_file = open(sys.argv[1], 'rb')
gns_file = open('../user_made_file/gns/gns_'+sys.argv[3]+'.txt', 'w')
gwas_line = gwas_file.readline()
gwas_line = gwas_file.readline()
while gwas_line:
	gwas_list = gwas_line.split('\t')
	num = gwas_list[0]
	pos = gwas_list[1]
	if num == '23':
		num = 'X'
	if num == '24':
		num = 'Y'
	print num
	#min_pos = int(pos) - range
	#max_pos = int(pos) + range
	for elm in genes[num]:
		min_elm = int(elm[0])-int(range)
		max_elm = int(elm[1])+int(range)
		if min_elm < int(pos) and max_elm > int(pos):
			if elm[2] != "":
				gns_file.write(elm[2]+'\t'+num+'.'+pos+'\n')
	gwas_line = gwas_file.readline()
gns_file.close()
gwas_file.close()