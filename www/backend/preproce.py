# First a bunch of data preparation commands.

def ret_float(flist,i,remove_unnamed = True):
    """
    Function that is called by other funcs. Returns a list of float scores from a gwa.
    @param flist: List of filenames to read from.
    @param i: Which column to take data from.
    @return: The concatenated data from column i for all the files in flist, in float format.
    """
    ret = []
    if remove_unnamed:
            thisdata = [ float(line.split('\t')[i]) for line in open(flist) if line[0] != 'i' and line.split('\t')[1] != '---'  ]
	    #modified here for appropriate headers
	    thisdata.pop(0)
            ret.extend(thisdata)
    else:
            thisdata = [ float(line.split('\t')[i]) for line in open(flist) if line[0] != 'i' ]
            thisdata.pop(0)
            ret.extend(thisdata)
    return ret

def ret_str(flist,i,remove_unnamed = True):
    """
    Function that is called by other funcs. Returns a list of float scores from a gwa.
    @param flist: List of filenames to read from.
    @param i: Which column to take data from.
    @param remove_unnamed: If True, removes the lines that have --- as rsid.
    @return: The concatenated data from column i for all the files in flist, in string format with newlines after.
    """
    ret = []
    if remove_unnamed:
            thisdata = [ '%s\n' %line.split('\t')[i] for line in open(flist) if line.split('\t')[1] != '---']
            thisdata.pop(0)
            ret.extend(thisdata)
    else:
            thisdata = [ '%s\n' %line.split('\t')[i] for line in open(list) ]
            thisdata.pop(0)
            ret.extend(thisdata)
    return ret

def frequentist_add(flist):
    return ret_float(flist,14)

def frequentist_gen(flist):
    return ret_float(flist,15)

def bayesian_add(flist):
    return ret_float(flist,2)

def bayesian_gen(flist):
    return ret_float(flist,17)

def good_clustering(flist):
    return ret_float(flist,20)

#-------------------------------------------------------------------

# This was used to generate snptest files:
def mysnps(mysnps, allsnps, outsnps):
    """
    Picks out all the snps in mysnps out of the snps in allsnps and puts them in outsnps.
    @param mysnps: filename of the file with all the snps in the wtccc data.
    @param allsnps: filename of ginormous file with all snps, with location and chromosome data. From ensembl.
    @para outfile: filename of the file to write to.
    """
    snps = {}
    for snp in open(mysnps):
        snps[snp.strip()] = snp.strip() # Add all snps to the hashtable.
    outdata = []
    for line in open(allsnps):
        try:
            snp,chrom,pos = line.split('\t')
            outdata.append("%s\t%s\t%s"  %(snps[snp],chrom,pos))
        except:
            pass
    out = open(outsnps,'w')
    out.writelines(outdata)

# These do what they claim to do.
def generemoveempty(fname, fout):
    """
    Small function to add null to all genes without entrez gene id. Replaces \t\t with \tnull\t.
    @param fname: file with all the gene data.
    @param fout: name of the file to write to.
    """
    lines = [line for line in open(fname) if line.count('\t\t') < 1]
    open(fout,'w').writelines( lines )

def genesplitchromosomes(fname):
    """
    Splits up fname into a bunch of files based on chromosome.
    @param fname: Name of the file which contains the data.
    """
    genes = (line for line in open(fname))
    chroms = {}
    for gene in genes:
        try:
            chroms[gene.split('\t')[-1]].append(gene)
        except KeyError:
            chroms[gene.split('\t')[-1]] = [gene]
    for chrom in chroms:
        open('gene_chrom_%s.txt' %(chrom.strip()),'w').writelines(chroms[chrom])

def snpsplitchromosomes(fname):
    """
    Splits up fname into a bunch of files based on chromosome.
    @param fname: Name of the file which contains the data.
    """
    snps = (line for line in open(fname))
    chroms = {}
    for snp in snps:
        try:
            chroms[snp.split('\t')[1]].append(snp)
        except KeyError:
            chroms[snp.split('\t')[1]] = [snp]
    for chrom in chroms:
        open('snp_chrom_%s.txt' %(chrom.strip()),'w').writelines(chroms[chrom])

def posterior(p_as, p_an, p_a):
    """
    Calculates the posterior probability of association.
    @param p_as: Probability of association for the snp given the score.
    @param p_an: Probability of association for the snp given the the extra data, like the network.
    @param p_a: Some nice probability for snps in general.
    @return: Posterior probability.
    """
    return ( p_as * p_an * (1-p_a) ) / ( p_as * p_an * (1-p_a) + (1-p_as)*(1-p_an)*p_a )

def snptest_grep(snptestprefix, martprefix, outprefix, chroms, report = True):
    """
    For each row in each snptest file, seeks finds the row (if any) in the martfiles with the same rsid.
    Prints all the rows for which it finds matches in a file with the right chrom name.
    @param snptestprefix: All the WTCCC files. Has format:
    id\\trsid\\tpos\\tallele1\\tallele2\\taverage_maximum_posterior_call\\tcontrols_AA\\tcontrols_AB\\tcontrols_BB\\tcontrols_NULL\\tcases_AA\\tcases_AB\\tcases_BB\\tcases_NULL\\tfrequentist_add\\tfrequentist_gen\\tbayesian_add\\tbayesian_gen\\tsex_frequentist_add\\tsex_frequentist_gen\\tgood_clustering\\n
    @param martprefix: List of all snps from biomart. Has format:
    Reference ID\\tChromosome Name\\tPosition on Chromosome (bp)\\n
    @param outprefix: Output file prefix. Has same format as biomart:
    Reference ID\\tChromosome Name\\tPosition on Chromosome (bp)\\n
    @param chroms: List of all the chromosomes. Treated differently by mart and snptest. snptest has 0n, mart has n.
    @param report: Whether to print out reports every now and then or not.
    """
    for chrom in chroms:
        f = open('%s_%02d.txt' %(snptestprefix, chrom))
        martlines = dict([ (line.strip().split('\t')[0], line) for line in open('%s_%d.txt' %(martprefix, chrom)) ])
        outlines = []
        if report:
            sys.stderr.write('%s\n' %chrom)
        for line in f:
            rsid = line.split('\t')[1]
            try:
                outlines.append(martlines[rsid])
            except KeyError:
                pass
        open('%s_%d.txt' %(outprefix, chrom),'w').writelines(outlines)

def genomedata(datadir):
    """
    Prepares all the indata for genome, below.
    @param datadir: Directory where the indata dwells.
    @return: Triplet with geneprefix, snpprefix,chroms
    """
    import os
    chroms = [ line[11:].split('.')[0] for line in os.listdir(datadir) if line[0:11] == 'gene_chrom_' ]
    chroms.remove('Chromosome Name')
    return datadir+'gene_chrom', datadir+'snptest', chroms

# Important code that is directly used in main.

def gene2snp(geneprefix, snpprefix, chroms, cutoffdistance, report = True):
    """
    Makes a dictionary that for each gene returns all a the snps up to a certain distance away.
    @param geneprefix: List of all genes. Has format:
    Ensembl Gene ID\\tEnsembl Transcript ID\\tEntrezGene ID\\tGene Start (bp)\\tGene End (bp)\\tChromosome Name\\n
    @param snpprefix: List of all snps. Has format:
    Reference ID\\tChromosome Name\\tPosition on Chromosome (bp)\\n
    @param chroms: List of all the chromosomes.
    @param cutoffdistance: Distance for what to count as the nearby region. Maybe one day it would be nice to differentiate
    between upstream and downstream.
    @param report: Whether to print out reports every now and then or not.
    @return: Dictionary with all the close snps for each gene.
    """
    import sys
    genes = {}
    for chrom in chroms:
        f = open('%s_%s.txt' %(geneprefix, chrom))
        if report:
            sys.stderr.write('gene2snp @ chromosome %s\n' %chrom)
        for line in f:
            snplines = ( line.strip().split('\t') for line in open('%s_%s.txt' %(snpprefix, chrom)) )
            geneits = line.strip().split('\t')
            genes[geneits[2]] = []
            genestart = int(geneits[3])
            genestop = int(geneits[4])
            for snpits in snplines:
                # Check if snp is within 1Mb of the gene.
                snppos = int(snpits[2])
                if snppos-genestart > 0:
                    if snppos-genestop < 0:
                        genes[geneits[2]].append(snpits[0])
                    elif snppos-genestart < cutoffdistance:
                        genes[geneits[2]].append(snpits[0])
                elif snppos-genestop < 0:
                    if genestart-snppos < 0:
                        genes[geneits[2]].append(snpits[0])
                    elif genestart-snppos < cutoffdistance:
                        genes[geneits[2]].append(snpits[0])
    return genes

def write_tdrs(fname,tdrs):
    """
    Takes an tdr dictionary and writes the tdrs derived from that to a file.
    @param fname: Name of output file.
    @param tdrs: True detection rate dictionary.
    """
    tdrnames = [(tdrs[gene],gene) for gene in tdrs]
    tdrnames.sort(reverse=True)
    print 'Writing tdrs to %s' %fname
    open(fname,'w').writelines(['%s\t%s\n' %(gene,tdr) for (tdr,gene) in tdrnames])
    print 'TDRs written. Exiting.'


# These are the only things really used:
def odds_dict(flist,good_cluster=True):
    """
    Creates a nice dictionary from all the ids to the corresponding Bayes factors of association. Uses the
    additive Bayes factors.
    @param flist: List of all files to look in. They should be of WTCCC standard format.
    @param good_cluster: True if only snps with good clustering should be used, False otherwise. Defaults to True.
    @return: Dictionary from ids to Bayes factors of association.
    """
    import numpy
    ids = ret_str(flist,0)
    bf = bayesian_add(flist)
    return dict([(ids[i].strip(),bf[i]) for i in range(len(ids))])

def p_val_odds_dict(flist,good_cluster=True):
    """
    Creates a nice dictionary from all the ids to the corresponding p-value odds of association. Uses the
    frequentist_add p-vals.
    @param flist: List of all files to look in. They should be of WTCCC standard format.
    @param good_cluster: True if only snps with good clustering should be used, False otherwise. Defaults to True.
    @return: Dictionary from ids to odds of association.
    """
    import numpy
    ids = ret_str(flist,1)
    bf = frequentist_add(flist)
    bf = [numpy.log10((1.-b)/b) for b in bf]
    clust = ret_float(flist,20)
    if good_cluster:
        return dict([(ids[i].strip(),bf[i]) for i in range(len(ids)) if clust[i] == 1.])
    else:
        return dict([(ids[i].strip(),bf[i]) for i in range(len(ids))])

def p_val_odds_dict_crohn(fname):
    """
    Creates a nice dictionary from all the ids to the corresponding p-value odds of association. Uses the
    frequentist_add p-vals.
    @param fname: List of the file to look in. Should be of the tab-delimited format given by the Crohn's meta-analysis.
    @return: Dictionary from ids to odds of association.
    """
    import numpy
    data = [ (line.split('\t')[0],float(line.split('\t')[-1])) for line in open(fname) if line[0] != 'S' ]
    return dict([(d[0],numpy.log10((1.-d[1])/d[1])) for d in data])


# These are written to deal with the hypertension gene set from
# http://cmbi.bjmu.edu.cn/genome/candidates/candidates.html

def id_parser(fname):
    """
    Reads all the ids in the file Homo_sapiens.gene_info, or another file with the same format, (from ncbi:
    ftp://ftp.ncbi.nih.gov/gene/DATA/GENE_INFO/Mammalia/Homo_sapiens.gene_info.gz) and returns a dictionary from common
    names to entrez ids.
    @param fname: Location of the file.
    @return: Dictionary, from common names (including synonyms) to entrez ids.
    """
    f = open(fname)
    f.readline()
    genes = ( (l.split('\t')[1], [l.split('\t')[2]],l.split('\t')[4].split('|')) for l in f if l.split('\t')[2]!='')
    ret = {}
    for (entrez_id, names,syns) in genes:
        names.extend(syns)
        for name in names:
            ret[name] = int(entrez_id)
    return ret

def hypertensiongenes(fname, id_dict):
    """
    Read a bunch of hypertension genes and returns their entrez ids.
    @param fname: Filename for hypertensiongenes.
    @param id_dict: Dict from common names to entrez ids.
    @return: Entrez ids.
    """
    f = open(fname)
    f.readline()
    return [id_dict[l.split('\t')[1]] for l in f if l.split('\t')[1] in id_dict]

def hprd_translator(fname,outfile,logodds=.5):
    """
    Translates an hprd net to the same format as Insuk's humannet.
    @param fname: Name of the file with the hprd network.
    @param outfile: Name of the output file where the new network is written.
    @param logodds: Estimated logodds of the connected genes sharing the same function.
    """
    edges = ( x.split('\t') for x in open(fname,'r') )
    def burk(s):
        print s
    edges.next() #remove the row with all the junk.
    lines = ['%s\t%s\t%s\n'%(A,B,logodds) for (nA,A,nB,B,exp_type,pubmed) in edges if A != 'None' and B != 'None']
    open(outfile,'w').writelines(lines)



# This takes out all the names of the loci.
def gene2band(fname):
    """
    Picks out all the genes in mygenes out of the genes in allgenes and returns a dict from id to band (e.g. 7q21).
    @param fname: filename of the file with all the genes looked at. From ensembl. Should have format
    Ensembl Gene ID\tEnsembl Transcript ID\tGene Start (bp)\tGene End (bp)\tBand\tStrand\tChromosome Name\tEntrezGene ID\\n. Is probably named Data/mart_export_gene_location.txt .
    @return: Dictionary with gene ids to positions.
    """
    lines = open(fname)
    lines.readline() # Remove the first line with all the junk.
    genes = dict([ (int(l[-1]),'%s%s'%(l[-2],l[-4])) for l in lines if l[-1] != '\n'])
    return genes
