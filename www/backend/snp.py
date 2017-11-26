import sys
import csv
import re
import math

gwas_file = open(sys.argv[1], 'rb')
gns_file = open('../user_made_file/snp/snp_pvalue_'+sys.argv[2]+'.txt', 'w')
gwas_line = gwas_file.readline()
gwas_line = gwas_file.readline()
while gwas_line:
	gwas_list = gwas_line.split('\t')
	num = gwas_list[0]
	pos = gwas_list[1]
	p_val = float(gwas_list[2])
	if p_val > 0 :
		log_p = -1*math.log(p_val,10)
		gns_file.write(num+'.'+pos+'\t'+str(p_val)+'\t'+str(log_p)+'\n')
	gwas_line = gwas_file.readline()
gns_file.close()
gwas_file.close()