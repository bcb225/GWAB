import sys
import csv
import re
import subprocess
import bisect
range = 100000
#gns_071e39adaaeda7d150a4a09b3452382d.txt
#range = sys.argv[4]
snp = dict()
gwas_file = open('gwas_071e39adaaeda7d150a4a09b3452382d.txt', 'rb')
#gwas_file = open(sys.argv[1], 'rb')
#gns_file = open('../user_made_file/gns/gns_'+sys.argv[3]+'.txt', 'w')
gwas_line = gwas_file.readline()
gwas_line = gwas_file.readline()
while gwas_line:
	gwas_list = gwas_line.split('\t')
	num = gwas_list[0]
	if num == 23:
		num = 'X'
	if num == 24:
		num = 'Y'
	pos = int(gwas_list[1])
	if num in snp:
		snp[num].append(pos)
	else:
		#print chr_detect[0]
		snp[num] = []
		snp[num].append(pos)
	gwas_line = gwas_file.readline()

for k,v in snp.items():
	v.sort(key=int)
	print k
	print v

gene_file = open('../files/knownGeneHG18.csv','rb')
#gene_file = open(sys.argv[2],'rb')
reader = csv.reader(gene_file)
gns_file = open('test_gns.txt', 'w')
for row in reader:
	#row[1] = chr_num
	#row[3] = start & row[4] = end
	#row[11] = align_id
	p = re.compile('(\d+|x|y|X|Y|M)')
	chr_detect = p.findall(row[1])
	min_pos = int(row[3])-int(range)
	max_pos = int(row[4])+int(range)
	if chr_detect[0] in snp and row[11] != '':
		a = int(bisect.bisect_left(snp[chr_detect[0]],min_pos))
		b = int(bisect.bisect_right(snp[chr_detect[0]],max_pos))-1
		print "chr is " + str(chr_detect[0])
		print "gene num is " + str(row[11])
		print "list length is "+str(len(snp[chr_detect[0]]))
		print "a is " + str(a) + " b is " + str(b)
		if a <= b:
			print 'min pos is   '+str(min_pos) +' and max pos is '+str(max_pos)+'\nsnp start is '+str(snp[chr_detect[0]][a])+' and snp end is '+str(snp[chr_detect[0]][b])+'\n'
			count = a
			if count <= b :
				gns_file.write(str(row[11])+'\t'+str(chr_detect[0])+'.'+str(snp[chr_detect[0]][count])+'\n')
				++count
				print 'count is ' + str(count)
			max_index = len(snp[chr_detect[0]])-1
gns_file.close()
gwas_file.close()