"""
This library is wicked awesome, and deals with humannets. F'sure.
"""
import numpy as np
import os,sys

class softgba:
    """
    This class contains all the data needed to run the soft category assignment GBA.
    """
    def __init__(self, fname, bayesfactors, f_g2s):
        """
        Constructs the network.
        @param fname: Name of the network file.
        @param bayesfactors: All the Bayes factors for all the snps.
        @param g2s: A dict from gene name to list of all nearby snps.
        """
 	# Construct g2s dict - modified by shim
	gene2snps = (line for line in open(f_g2s))
	g2s = {}
	for gene2snp in gene2snps:
		try:
			g2s[gene2snp.split('\t')[0].strip()].append(gene2snp.split('\t')[1].strip())
		except KeyError:
			g2s[gene2snp.split('\t')[0].strip()] = [gene2snp.split('\t')[1].strip()]
        # Construct a list of all the genes present in the gwas.
        genes = sorted([g for g in g2s.keys() if len(g2s[g])>0])
        g2r = dict([(gene,i) for (i,gene) in enumerate(genes)])
        # Construct the adjacency matrix. All the edges in the network file are given in base e:
        ln10 = np.log(10)
        self.edges = [(a,b,float(s)/ln10) for (a,b,s) in (l.split('\t') for l in open(fname,'r'))]
        self.L = np.matrix(np.zeros((len(genes),len(genes)), dtype=np.float32))
        for (a,b,s) in self.edges:
            try:
                self.L[g2r[a],g2r[b]]=s
                self.L[g2r[b],g2r[a]]=s
            except KeyError:
                pass
        # Construct the snp and Bayes factor vectors.
        # This finds the _strongest_ snp close to each gene.
        self.g2snp = {}
        self.b = np.zeros(len(genes))
        for gene in genes:
            #print gene
            #sys.exit()
            #print g2s[gene]
            #sys.exit()
            list_temp = []
            for snp in g2s[gene] :
                if snp in bayesfactors : 
                    #print [((bayesfactors[snp],snp) if snp in bayesfactors else None) for snp in g2s[gene]]
                    #sys.exit()
                    list_temp.append((bayesfactors[snp],snp))
                    #print bayesfactors[snp],snp
                    #sys.exit()
            if len(list_temp) > 0 :
                #print max(list_temp)
                (bf,snp) = max(list_temp)
                
            #(bf,snp) = max([((bayesfactors[snp],snp) if snp in bayesfactors else None) for snp in g2s[gene]])
            
                self.b[g2r[gene]] = bf
                self.g2snp[gene] = snp
            self.g2r = g2r
            self.preds = self.b
            self.genes = genes
    
    def prior_adjustment(self, prior):
        """
        When you want to change the prior, you need to recalculate the weights and
        the posteriors.
        @param prior: The prior logodds of association. Should probably be around 1/10,000 (-4 in log10) based
        on 1,000,000 independent regions in the genome and about 100 loci involved.
        """
        self.prior = prior
        posterior = self.b+prior
        # Calculate the soft assignment scores 'a'
        a = np.where(posterior>0,(1-10**-posterior)/(1+10**-posterior),0.)
        a = np.matrix(a).T
        self.preds = self.L*a+np.matrix(self.b).T
    
    def predictions(self):
        return [(g, i) for (i,g) in sorted(zip(self.preds[:,0],self.genes),reverse=True)]

    def predictions_auc(self):
        #return [(g, i) for (i,g) in sorted(zip(self.preds[:,0],self.genes),reverse=True)]
        return [g for (i,g) in sorted(zip(self.preds[:,0],self.genes),reverse=True)]

    
    def shuffle(self):
        """
        This method randomizes the network, by shuffling all the geneids around.
        """
        from random import randint
        # First shuffle the network:
        genes = self.genes
        translator = {}
        for (a,b,s) in self.edges:
            translator[a] = a
            translator[b] = b
        keys = translator.keys()
        newkeys = []
        while len(keys) != 0:
            newkeys.append(keys.pop(randint(0,len(keys)-1)))
        keys = translator.keys()
        translator = {}
        for i in range(len(keys)):
            translator[keys[i]] = newkeys[i]
        self.edges = [(translator[A],translator[B],s) for (A,B,s) in self.edges]
        # Now construct the ajacency matrix:
        self.L = np.matrix(np.zeros((len(genes),len(genes)), dtype=np.float32))
        for (a,b,s) in self.edges:
            try:
                self.L[self.g2r[a],self.g2r[b]]=s
                self.L[self.g2r[b],self.g2r[a]]=s
            except KeyError:
                pass
    
    def write_report(self,outfile,genesymbols):
        """
        Writes out all the candidates to a file.
        @param outfile: Name of the output file.
        @param genenames: A file with entrez ids to gene symbols.
        """
        predorder = sorted(zip(self.preds.flatten().tolist(), self.genes))
        originalorder = enumerate(sorted(zip(self.b.flatten().tolist(), self.genes)))
        originalorder = dict([(g,i+1) for (i,(s,g)) in originalorder])
        out = open(outfile,'w')
        g2r = self.g2r
        symbols = open(genesymbols)
        symbols.readline() # Remove header
        g2n = dict([(l[10].strip(),l[1]) for l in (l.split('\t') for l in genenames)])
        out.writeline("Rank\tOriginal rank\tGene symbol\tEntrez ID\tNew score\tOriginal score\tBoost weight\n")
        for i,g in enumerate(predorder):
            info = (i+1,originalorder[g],g2n[g],g,self.preds[g2r[g]],self.b[g2r[g]],self.a[g2r[g]])
            out.writeline("%s\t%s\t%s\t%s\t%s\t%s\t%s\n"%info)


#def testnet(disease, network='./AraNetV2', g2s='ID2'):
def testnet(disease, network, g2s, flist) :
#def testnet(disease, network='./AraNetV2', g2s='test_g2s.txt'):
    """Constructs a softgba object with reasonable defaults.
    @param disease: Which disease to work with.
    @param network: File with the network.
    @param g2s: Pickle with a dictionary, from genes to lists of snps."""
    import cPickle
    import preproce
    #flist = 'col2'
    odds = preproce.odds_dict(flist)
    #print odds
    return softgba(network, odds, g2s)


def frequentist_testnet(disease, network='./hs_18714geneid_IntNet.lls'):
        """
        Constructs a humannet with nice defaults.
        @param disease: Which disease to work with.
        @param network: File with the network.
        """
        import cPickle
        import preproce
        disease = 'basic/snptest_%s_' %disease
        g2s = cPickle.load(open('g2s1e4.pickle'))
        flist = [ "%s%02d.txt" %(disease,i) for i in range(1,23)]
        odds = preproce.p_val_odds_dict(flist)
        return softgba(network, odds, g2s)
