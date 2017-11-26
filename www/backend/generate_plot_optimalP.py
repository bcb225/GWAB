#modified for 
#modified for only one phenototype (Dec. 21. 2012) by shim
#recovering the function to find optimal p-value threshold (Mar. 17. 2014) by shim
import gwasgba as bayesnet
import rocabilly
import pylab
import numpy
import pickle
import datetime
import plac
import os,sys
import re
# modified for finding the optimal threshold

@plac.annotations(
shuffles=("Number of shuffles", 'positional', None, int),
outfile=("File to write output to"),
fpr=("FPR cutoff", 'option', 'f', float),
genelist=("genelistinput"),
network=("networkinput"),
g2s=("chr_pos file"),
phenotype=("phenotype name"),
boost=("SNP pvalue file for boosting"), #forboost_incremental file
range_start =("p_value start", 'positional',None,float),
range_end=("p_value end", 'positional', None,float),
stepsize=("p_value step", 'positional', None,float),
u_key=("user_key")
)


def main(shuffles,outfile,genelist,network,g2s,phenotype,boost,range_start,range_end,stepsize,u_key,fpr=.05):
#def main(shuffles,outfile,genelist,network,g2s,phenotype,boost,fpr=1):
	"""Plots the ROC AUC for the net predictions for a number of different priors, compares them to the predictions of a number of shuffled nets with the same priors and plots it all in a nice plot."""
	filename = '../user_made_file/result/'+u_key+'_opt'
	phenotype = phenotype.decode('string_escape')
	fileout = open(filename,"w")
	f = pylab.figure()
	roc = rocabilly.pocker(genelist)
    	# Then make the right kind of net.
    	net = bayesnet.testnet(phenotype, network, g2s, boost)
    	# Choose range for priors.
    	#stepsize = .3
    	#range_start = -6.
    	#range_end = 1.
    	priors = numpy.arange(range_start,range_end+stepsize,stepsize) # +stepsize on end of range for inclusive range
    	#netpredict = []
	auc_real = []
    	def new_auc(prior):
        	net.prior_adjustment(prior)
    		#return net.predictions()
		return roc.auc(net.predictions_auc(), fpr_cut=fpr)
    	#netpredict = [new_auc(-3)]
	auc_real = [new_auc(prior) for prior in priors]
	maxauc = auc_real.index(max(auc_real))
	print >> fileout , "%s\t%f" % (genelist , priors[maxauc]) 
	# Then calculate a number of shuffled nets and make the aucs.
        prior = priors[maxauc]
        net.prior_adjustment(prior)
        netpredict = [net.predictions()]
        list_preds = []
        for netpreds in netpredict :
            for nets in netpreds :
                parama =  str(nets).split(",")[0].strip("(").strip("'")
                paramb =  str(nets).split(",")[1].strip("matrix([[ ").strip("]]))")
                list_preds.append(parama+"\t"+paramb)

        out = "../user_made_file/result/genelist_%s.output" % (u_key)
        file_out = open(out, "w")
        for netslist in list_preds :
            file_out.write(netslist)
            file_out.write("\n")
        file_out.close()

    	#list_preds = []
    	#for netpreds in netpredict :
    	#    for nets in netpreds :
    	#        parama =  str(nets).split(",")[0].strip("(").strip("'")
    	#        paramb =  str(nets).split(",")[1].strip("matrix([[ ").strip("]]))")
    	#        list_preds.append(parama+"\t"+paramb)
    	#file_out = open('SCZ(-3).output', 'w')
    	#for netslist in list_preds :
    	#    file_out.write(netslist)
    	#    file_out.write("\n")
    	#file_out.close()    

	auc_shuffle = []
    	for n in range(shuffles):
        	now = datetime.datetime.now()
        	#print '%s-%s\t%s:%s\t@ shuffle %s.' %(now.month,now.day,now.hour,now.minute,n)
        	net.shuffle()
        	auc_shuffle.append([new_auc(prior) for prior in priors])
    	auc_shuffle = numpy.asarray(auc_shuffle).T
    	baseline = roc.auc([g for (i,g) in sorted(zip(net.b,net.genes),reverse=True)],fpr_cut=fpr)
    	mean = auc_shuffle.mean(1)
    	sigma = numpy.sqrt(auc_shuffle.var(1))
    	pickle.dump( (priors,auc_real,auc_shuffle,baseline,mean,sigma), open('%s.pickle'%outfile,'w') )
    	pylab.plot(priors,mean,'k:',linewidth=1.5,label='Mean of shuffled networks')
    	pylab.plot(priors,mean+2*sigma,'k-',linewidth=1.5,label='_nolegend_')
    	pylab.plot(priors,mean-2*sigma,'k-',linewidth=1.5,label='_nolegend_')
    	pylab.fill(numpy.hstack((priors,priors[::-1])),numpy.hstack((mean+2*sigma,(mean-2*sigma)[::-1])),
        	'.8',linewidth=0.,label='Two standard deviations for shuffled networks')
    	pylab.plot(priors,auc_real,'-r',linewidth=1.5,label='Network-augmented GWAS')
    	pylab.plot([priors[0],priors[-1]],[baseline,baseline],'b--',linewidth=1.5,label='GWAS Baseline')
    	pylab.title(phenotype)
        pylab.xlabel("p-value threshold")
        pylab.ylabel("Area under ROC curve (<5% FPR)")
    	pylab.legend(loc=3)
    	pylab.draw()
    	pylab.axis(xmax=priors[-1])
    	f.savefig(outfile+'.png')

    	
if __name__ == "__main__":
   	plac.call(main)
