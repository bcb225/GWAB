"""
These functions are intended to handle omim data and to plot nice
roc-plots.
"""
import sys


class rocker:
    """
    Class to hold all the things one might need from omim.
    """
    def __init__(self,ids):
        """
        @param ids: List of (entrez) ids. Make sure that they are all in your network!
        """
        self.entrezids = ids
    
    def trim_ids(self,candidates):
        """
        Trims out "true hits" that are not in the set of candidates.
        @param candidates: The set of candidates.
        """
        test = self.entrezids[:]
        for gene in test:
            if gene not in candidates:
                self.entrezids.remove(gene)
    
    def roc_plot(self,candidates,lab='Predictions',col='g-'):
        """
        Draws a rocplot.
        @param candidates: A list of the candidate genes, ordered from least to most likely.
        @param lab: Label for the line.
        @param col: Color and symbol for the line.
        @return: Returns the area under the curve.
        """
        # Todo: Fix so that missed ones etc are reported, as in Kris's webtool.
        import pylab
        tp = [0]
        fp = [0]
        for gene in candidates:
            if gene in self.entrezids:
                tp.append(tp[-1]+1)
                fp.append(fp[-1])
            else:
                tp.append(tp[-1])
                fp.append(fp[-1]+1)
        tpr = pylab.array(tp)/float(tp[-1])
        fpr = pylab.array(fp)/float(fp[-1])
        pylab.plot(fpr,tpr,col,label=lab,linewidth=2)
        pylab.plot([0,1],[0,1],'k',label='_nolegend_')
        auc = tpr.sum()/len(tpr)
        pylab.xlabel('False positive ratio')
        pylab.ylabel('True positive ratio')
        return auc
    
    def auc(self,candidates,cutoff=False,measure=False,fpr_cut=False):
        """
        Calculate auc without drawing rocplot.
        @param candidates: A list of the candidate genes, ordered from least to most likely.
        @param cutoff: If not false, only count the first cutoff hits.
        @param measure: If not false, integrate with this weight.
        @param fpr_cut: If not false, cut off at this fpr.
        @return: Returns the area under the curve.
        """
        # Todo: Fix so that missed ones etc are reported, as in Kris's webtool.
        import pylab
        tp = [0]
        fp = [0]
        for gene in candidates:
            if gene in self.entrezids:
                tp.append(tp[-1]+1)
                fp.append(fp[-1])
            else:
                tp.append(tp[-1])
                fp.append(fp[-1]+1)
        tpr = pylab.array(tp)/float(tp[-1])
        fpr = pylab.array(fp)/float(fp[-1])
        if cutoff:
            return tpr[0:cutoff].sum()/cutoff
        elif measure is not False:
            tpr = tpr*measure
            return tpr.sum()
        elif fpr_cut is not False:
            tpit = iter(tpr)
            fpit = iter(fpr<fpr_cut)
            # Wohoo. Functional magic!
            hits = [tpit.next() for i in fpit if i]
            #return pylab.asarray(hits).sum()/13745.
            #return pylab.asarray(hits).sum()/len(hits)
            return pylab.asarray(hits).sum()/len(tpr)
        else:
            return tpr.sum()/len(tpr)
    
    def prec_rec_plot(self,candidates,lab='Predictions',col='g-'):
        """
        Plots precision versus recall.
        @param candidates: A list of the candidate genes, ordered from least to most likely.
        """
        import pylab
        precs = []
        recs = []
        tp = 0. # True positives
        rp = float(len(self.entrezids)) # Real positives
        fp = 0. # False positives
        for gene in candidates:
            if gene in self.entrezids:
                tp += 1.
            else:
                fp += 1.
            precs.append(tp/(tp+fp))
            recs.append(tp/rp)
        pylab.plot(recs,precs,col,label=lab,linewidth=2)
        pylab.xlabel('Recall')
        pylab.ylabel('Precision')
    
    def sens_spec_plot(self,candidates,lab='Predictions',col='g-'):
        """
        Plots sensitivity versus specificity.
        @param candidates: A list of the candidate genes, ordered from least to most likely.
        @param lab: Label for the line.
        @param col: Color and symbol for the line.
        """
        import pylab
        sens = []
        spec = []
        tp = 0. # True positives
        rp = float(len(self.entrezids)) # Real positives
        tn = float(len(candidates))-rp # Everything is classified as negative to start off with,
        rn = tn                        # so all the true negatives are correctly classified.
        for gene in candidates:
            if gene in self.entrezids:
                tp += 1.
            else:
                tn -= 1.
            sens.append(tp/rp)
            spec.append(tn/rn)
        pylab.plot(sens,spec,col,label=lab,linewidth=2)
        pylab.xlabel('Sensitivity')
        pylab.ylabel('Specificity')
    
    def precision_at_recall(self,candidates,recall):
        """
        Calculate the precision at a given recall.
        @param candidates: A list of the candidate genes, ordered from least to most likely.
        @param recall: The minimum recall.
        @return: Precision at the least number of hits needed to reach the sought recall.
        """
        # Todo: Fix so that missed ones etc are reported, as in Kris's webtool.
        import pylab
        # Initiate true and false positives and negatives
        tp = 0. # True positives
        rp = float(len(self.entrezids)) # Real positives
        fp = 0. # False positives
        for gene in candidates:
            if gene in self.entrezids:
                tp += 1.
            else:
                fp += 1.
            if tp/rp > recall:
                return tp/(tp+fp)
        return 0.
    
    def report_hits(self,candidates,report):
        """
        Reports a the first report hits in candidates.
        @param candidates: The list of candidates.
        @param report: How many candidates to report.
        @return: List of report tuples, with position and ids.
        """
        hits = []
        for i in range(len(candidates)):
            gene = candidates[i]
            if gene in self.entrezids:
                hits.append((gene,i))
                if len(hits) > report:
                    break
        return hits
    
    def prec_rec_plot_file(self,fname,report=False,col=1):
        """
        Takes a file of hits in tab delimited format where the hits are ordered from least to most likely,
        and makes a roc plot out of it.
        @param fname: Name of file in standard output format for gwaboost.py
        @param report: If set to a number the program returns the first n hits, otherwise False.
        @param col: Which column to base the predictions on.
        @return: If report is a number, return that number of hits.
        """
        file = open(fname)
        params = file.readline()
        col_ids = file.readline()
        candidates = [(float(line.split('\t')[col]), int(line.split('\t')[0])) for line in file]
        candidates.sort(reverse=True)
        candidates = [cand[1] for cand in candidates]
        self.prec_rec_plot(candidates)
        if report:
            return self.report_hits(candidates,report)
        return True

    def sens_spec_plot_file(self,fname,report=False,col=1):
        """
        Takes a file of hits in tab delimited format where the hits are ordered from least to most likely,
        and makes a sensitivity vs. specificity plot out of it.
        @param fname: Name of file in standard output format for gwaboost.py
        @param report: If set to a number the program returns the first n hits, otherwise False.
        @param col: Which column to base the predictions on.
        @return: If report is a number, return that number of hits.
        """
        file = open(fname)
        params = file.readline()
        col_ids = file.readline()
        candidates = [(float(line.split('\t')[col]), int(line.split('\t')[0])) for line in file]
        candidates.sort(reverse=True)
        candidates = [cand[1] for cand in candidates]
        self.sens_spec_plot(candidates)
        if report:
            return self.report_hits(candidates,report)
        return True

    def roc_plot_file(self,fname,report=False,col=1):
        """
        Takes a file of hits in tab delimited format where the hits are ordered from least to most likely,
        and makes a roc plot out of it.
        @param fname: Name of file in standard output format for gwaboost.py
        @param report: If set to a number the program returns the first n hits, otherwise False.
        @param col: Which column to base the predictions on.
        @return: If report is a number, return that number of hits. Else return AUC.
        """
        file = open(fname)
        params = file.readline()
        col_ids = file.readline()
        candidates = [(float(line.split('\t')[col]), int(line.split('\t')[0])) for line in file]
        candidates.sort(reverse=True)
        candidates = [cand[1] for cand in candidates]
        auc = self.roc_plot(candidates)
        if report:
            return self.report_hits(candidates,report)
        return auc

    def roc_plot_bayesnet(self,net,prior,report=False,label='Predictions',color='g-',classifier=1):
        """
        Takes a bayesnet object and makes a roc plot for it.
        @param net: Bayesnet object.
        @param prior: Prior logodds of association.
        @param report: If set to a number the program returns the first n hits, otherwise False.
        @param label: Label for the line.
        @param color: Color and style of the line.
        @param classifier: Whether to use the leery or naive classifier. Default is 1 for naive, 0 gives leery.
        @return: If report is a number, return that number of hits. Else return AUC.
        """
        net.prior_adjustment(prior)
        candidates = [(net.snps[node][classifier],node) for node in net.nodes()]
        candidates.sort(reverse=True)
        candidates = [cand[1] for cand in candidates]
        auc = self.roc_plot(candidates,lab=label,col=color)
        if report:
            return self.report_hits(candidates,report)
        return auc

    def correlation_curve_file(self,fname,colx=1,coly=2):
        """
        Takes a file of hits in tab delimited format where the hits are ordered from least to most likely,
        and plot a log log scatter plot of one column of data against another.
        @param fname: Name of file in standard output format for gwaboost.py
        @param report: If set to a number the program returns the first n hits, otherwise False.
        @param colx: First column to scatter stuff from.
        @param coly: Second column to scatter stuff from.
        @return: The data in colx and coly, as log numpy arrays.
        """
        import pylab
        file = open(fname)
        params = file.readline()
        col_ids = file.readline().split('\t')
        candidates = [(float(line.split('\t')[colx]), float(line.split('\t')[coly])) for line in file]
        candidates.sort(reverse=True)
        #def ceil(x):
            #if x < 1e-15:
                #return 1e-15
            #else:
                #return x
        col0 = pylab.asarray([cand[0] for cand in candidates]) #pylab.log([ceil(cand[0]) for cand in candidates])
        col1 = pylab.asarray([cand[1] for cand in candidates]) #pylab.log([ceil(cand[1]) for cand in candidates])
        pylab.plot(col0,col1,'go')
        pylab.xlabel(col_ids[colx])
        pylab.ylabel(col_ids[coly])
        return col0,col1
    
    def webreport(self,fname,number_of_reports,outfile,sortby=1):
        """
        Generates a html page with all the stuff you need.
        @param fname: Name of the output data file.
        @param number_of_reports: The number of genes to include in the report.
        @param outfile: Name of the html report file. Include the .html!
        @param sortby: The column to sort the data by. Col1=Boost, col2=wellcome b.f. col3=netscore.
        """
        file = open(fname)
        params = file.readline()
        col_ids = file.readline()
        boosts = [line.split('\t') for line in file]
        def cmp_list(x, y):
            if float(x[sortby]) < float(y[sortby]):
                return -1
            elif float(x[sortby]) > float(y[sortby]):
                return 1
            else:
                return 0
        boosts.sort(reverse=True, cmp = cmp_list)
        [boosts[i].append(i+1) for i in range(len(boosts))]
        outlines = []
        preamble = open('./Webreport/pagehead.html').readlines()
        def rowmaker(boost):
            if int(boost[0]) in self.entrezids:
                return '<tr class="verified"> <td>%s</td> <td><a href= "http://www.ncbi.nlm.nih.gov/sites/entrez?db=gene&cmd=search&term=%s" target="_blank">%s</a></td> <td>%s</td> <td>%s</td> <td>%s</td></tr>\n' %(boost[5],boost[0],boost[1],boost[2],boost[3],boost[4])
            else:
                return '<tr class="prediction"> <td>%s</td> <td><a href= "http://www.ncbi.nlm.nih.gov/sites/entrez?db=gene&cmd=search&term=%s" target="_blank">%s</a></td> <td>%s</td> <td>%s</td> <td>%s</td></tr>\n' %(boost[5],boost[0],boost[1],boost[2],boost[3],boost[4])
        otherlines = [ rowmaker(boost) for boost in boosts[0:number_of_reports] ]
        tablehead = open('./Webreport/tablehead.html').readlines()
        postamble = open('./Webreport/pagetail.html').readlines()
        outlines.extend(preamble)
        outlines.extend([params])
        outlines.extend(tablehead)
        outlines.extend(otherlines)
        outlines.extend(postamble)
        outfile = open('./Webreport/%s' %outfile,'w')
        outfile.writelines(outlines)
        outfile.close()
    

class omim(rocker):
    """
    Class to hold all the things one might need from omim.
    """
    def __init__(self,fname):
        """
        @param fname: Name of the file. The format is what you get when you save an omim webpage as text.
        """
        file = open(fname)
        entrezids = [int(line.split(':')[1]) for line in file if line.find('GeneID') != -1]
        file.close()
        rocker.__init__(self,entrezids)
        numbers = ['0','1','2','3','4','5','6','7','8','9']
        file = open(fname)
        self.shortnames = [line.split(':')[1] for line in file if line[0] in numbers]
        file.close()
    
    def add_data(self,fname):
        """
        Adds another data file to the gold standard used.
        @param fname: Name of the file. The format is what you get when you save an omim file as text.
        """
        file = open(fname)
        self.entrezids.extend( [int(line.split(':')[1]) for line in file if line.find('GeneID') != -1] )
        file.close()
        numbers = ['0','1','2','3','4','5','6','7','8','9']
        file = open(fname)
        self.shortnames.extend( [line.split(':')[1] for line in file if line[0] in numbers] )
        file.close()
    
class locker(rocker):
    """
    Class to hold all the things one might need from omim.
    """
    def __init__(self,fname):
        """
        @param fname: Name of the file with entrez ids in a row.
        """
        file = open(fname)
        entrezids = [int(line) for line in file]
        file.close()
        rocker.__init__(self,entrezids)
    


class pocker(rocker):
    """
    Class to hold all the things one might need from omim. Keeps the ids as strings.
    """
    def __init__(self,fname):
        """
        @param fname: Name of the file with entrez ids in a row.
        """
        file = open(fname)
        entrezids = [line.strip() for line in file]
        file.close()
        rocker.__init__(self,entrezids)
    




def heatmap(fname,interpolation='nearest'):
    """
    Makes a heatmap. This is very rough, should have lots of more functions.
    """
    import pylab
    import numpy
    origin = 'lower'
    f = open(fname)
    title = f.readline().split('_')[1]
    f.readline()
    # Format of file is time\tauc\tgeneprior\tnetprior\tscale\n
    data = [(float(l.split('\t')[1]),l.split('\t')[2],l.split('\t')[3]) for l in f]
    m = len(data)
    n = int(numpy.sqrt(len(data)))
    image = numpy.zeros((n,n))
    for i in range(n):
        for j in range(n):
            try:
                image[i,j] = data[i*n+j][0]
            except:
                pass
    try:
        pylab.imshow(image,interpolation=interpolation,origin=origin,cmap=pylab.cm.gist_heat)
    except:
        print interpolation, origin
        raise
    pylab.xlabel('Net prior')
    pylab.ylabel('Gene prior')
    xticks = [float(d[2]) for d in data]
    xticks.sort()
    yticks = [float(d[1]) for d in data]
    yticks.sort()
    pylab.xticks( [0,n/2,n], [str(e+10000-10000) for e in [xticks[0],xticks[m/2],xticks[-1]]] )
    pylab.yticks( [0,n/2,n], [str(e+10000-10000) for e in [yticks[0],yticks[m/2],yticks[-1]]] )
    pylab.title(title+' modified AUC')
    pylab.colorbar()



def doublehist(list1,list2,bins=10):
    import pylab
    y1,x1,rest = pylab.hist(list1,bins=bins,normed=True)
    y2,x2,rest = pylab.hist(list2,bins=x1,normed=True)
    width = (x1[0]-x1[1])/2.
    p1 = pylab.bar(x1, y1, width, color='r')
    p2 = pylab.bar(x1+width, y2, width, color='y')

def ekreo(list1,title=False,xlabel=False,rands=False,color='+',figure=False):
    """
    Draws an "ekreogram" -- plots the values of list1 on one axis and a normal r.v. on the other.
    From gr. ekreo, flow out or forth, shed, drop (of feathers) ...
    @param list1: Data to be plotted.
    @param figure: Either False or a handle to an active figure.
    @return: Pylab figure handle.
    """
    import pylab
    if not figure:
        figure = pylab.figure()
    pylab.yticks([])
    if title:
        pylab.title(title)
    if xlabel:
        pylab.xlabel(xlabel)
    if rands is not False:
        pylab.plot(list1,rands,color)
    else:
        pylab.plot(list1,pylab.randn(len(list1))**2,color)
    return figure



def make_graph(E,pos=False):
    """
    Draws a nice network with the edges E.
    @param E: The edges of the graph.
    @param pos: Whether to return the pos or not. If 'ret', returns the pos. If anything but 'new' or 'ret', uses the argument as a pos.
    @return: Pylab figure handle.
    """
    import networkx
    import pylab
    import random
    f = pylab.figure()
    G = networkx.Graph()
    G.add_edges_from(E)
    for node in G.nodes():
        if len(G.edges(node))==0:
            G.delete_node(node)
    if pos is False:
        pos=networkx.graphviz_layout(G,prog="neato")
    # Draw alternative layout:
    # draw nodes
    C=networkx.connected_component_subgraphs(G)
    colors = ['#0050D0', '#0060D0', '#0070D0', '#0080D0', '#0090D0', '#00A0D0', '#00B0D0', '#00C0D0', '#0050FF', '#0060FF', '#0070FF', '#0080FF', '#0090FF', '#00A0FF', '#00B0FF', '#00C0FF', 'darkblue', 'burlywood', 'darkorange', 'forestgreen', 'darkgray', 'dimgray', 'dodgerblue', 'olivedrab', 'chocolate', 'purple', 'lime', 'darkcyan', 'navy', 'darkslategray', 'teal', 'darkgreen', 'yellowgreen', 'saddlebrown', 'slateblue', 'chartreuse', ]
    for g in C:
        networkx.draw_networkx_nodes(g,pos,node_size=600,
            node_color = colors.pop(), vmin=0.0, vmax = 1.0,alpha = 0.8)
        networkx.draw_networkx_labels(G,pos,font_size = 8)
    # draw edges of different thickness
    networkx.draw_networkx_edges(G,pos,width=2)
    # draw labels
    pylab.xticks([])
    pylab.yticks([])
    return f,pos



def network_graph(net,title,names=False,logodds_cutoff=0.):
    """
    Draws a nice graph of all the genes with positive logodds for the relevant disease.
    @param net: A Bayesnet object.
    @param title: Titles of the graphs. Will be preappended with WTCCC and GBA.
    @param names: Dictionary from the entrez gene ids used in the net to other names.
    @param logodds_cutoff: Cutoff for logodds score needed to be drawn.
    @return: Handles to the two figures.
    """
    # Start out with the leery preds.
    import networkx
    import pylab
    H = networkx.Graph()
    edges = net.edges([node for node in net.nodes() if net.snps[node][1] > logodds_cutoff])
    H.add_edges_from([(A,B) for (A,B,s) in edges])
    # Remove stuff not in the candidate set.
    for node in H.nodes():
        try:
            if net.snps[node][1] < logodds_cutoff:
                H.delete_node(node)
        except:
            pass
    if names is not False:
        for node in H.nodes():
            try:
                if names[node]=='':
                    names[node]=node
            except KeyError:
                names[node]=node
        f1,p = make_graph([(names[A],names[B]) for (A,B) in H.edges()])
    else:
        f1,p = make_graph(H.edges())
    f1.suptitle('%s GBA Predictions (%s total)'%(title,len(H.nodes())))
    H = networkx.XGraph()
    edges = net.edges([node for node in net.nodes() if net.snps[node][0] > logodds_cutoff])
    H.add_edges_from(edges)
    # Remove stuff not in the candidate set.
    for node in H.nodes():
        try:
            if net.snps[node][0] < logodds_cutoff:
                H.delete_node(node)
        except:
            pass
    if names is not False:
        f2,p = make_graph([(names[A],names[B],s) for (A,B,s) in H.edges()],p)
    else:
        f2,p = make_graph(H.edges(),p)
    f2.suptitle('%s WTCCC Predictions (%s total)'%(title,len(H.nodes())))
    return f1,f2




def network_differences(net,title,names=False,logodds_cutoff=0.):
    """
    Draws a nice graph of all the genes with positive logodds for the relevant disease.
    @param net: A Bayesnet object.
    @param title: Titles of the graphs. Will be preappended with Leery and Naive.
    @param names: Dictionary from the entrez gene ids used in the net to other names.
    @param logodds_cutoff: Cutoff for logodds score needed to be drawn.
    @return: Handles to the two figures.
    """
    import networkx
    import pylab
    all_nodes = networkx.XGraph()
    edges = net.edges([node for node in net.nodes() if net.snps[node][1] > logodds_cutoff])
    all_nodes.add_edges_from(edges)
    # Remove stuff not in the candidate set.
    for node in all_nodes.nodes():
        try:
            if net.snps[node][1] < logodds_cutoff:
                all_nodes.delete_node(node)
        except:
            pass
    for node in all_nodes.nodes():
        try:
            if len(all_nodes.edges(node))==0:
                all_nodes.delete_node(node)
        except:
            pass
    edges = all_nodes.edges()
    # Boosted genes that would have made it anyway.
    boost_nodes = networkx.XGraph()
    boost_nodes.add_edges_from(edges)
    # Genes that would not have made the cutoff except for the boost.
    saved_nodes = networkx.XGraph()
    saved_nodes.add_edges_from(edges)
    # Unboosted genes that still made it.
    raw_nodes = networkx.XGraph()
    raw_nodes.add_edges_from(edges)
    for node in all_nodes.nodes():
        if net.snps[node][1] == net.snps[node][0]:
            boost_nodes.delete_node(node)
            saved_nodes.delete_node(node)
        elif net.snps[node][0] > logodds_cutoff:
            saved_nodes.delete_node(node)
            raw_nodes.delete_node(node)
        else:
            boost_nodes.delete_node(node)
            raw_nodes.delete_node(node)
    # Trix with the names.
    if names is not False:
        for node in all_nodes.nodes():
            try:
                if names[node]=='':
                    names[node]=node
            except KeyError:
                names[node]=node
    if names is not False:
        an = networkx.XGraph()
        an.add_edges_from([(names[A],names[B],float(s)) for (A,B,s) in all_nodes.edges()])
        an.add_nodes_from([names[A] for A in all_nodes.nodes()])
        sn = networkx.XGraph()
        sn.add_edges_from([(names[A],names[B],float(s)) for (A,B,s) in saved_nodes.edges()])
        sn.add_nodes_from([names[A] for A in saved_nodes.nodes()])
        bn = networkx.XGraph()
        bn.add_edges_from([(names[A],names[B],float(s)) for (A,B,s) in boost_nodes.edges()])
        bn.add_nodes_from([names[A] for A in boost_nodes.nodes()])
        rn = networkx.XGraph()
        rn.add_edges_from([(names[A],names[B],float(s)) for (A,B,s) in raw_nodes.edges()])
        rn.add_nodes_from([names[A] for A in raw_nodes.nodes()])
    else:
        an = networkx.XGraph()
        an.add_edges_from([(A,B,float(s)) for (A,B,s) in all_nodes.edges()])
        an.add_nodes_from([A for A in all_nodes.nodes()])
        sn = networkx.XGraph()
        sn.add_edges_from([(A,B,float(s)) for (A,B,s) in saved_nodes.edges()])
        sn.add_nodes_from([A for A in saved_nodes.nodes()])
        bn = networkx.XGraph()
        bn.add_edges_from([(A,B,float(s)) for (A,B,s) in boost_nodes.edges()])
        bn.add_nodes_from([A for A in boost_nodes.nodes()])
        rn = networkx.XGraph()
        rn.add_edges_from([(A,B,float(s)) for (A,B,s) in raw_nodes.edges()])
        rn.add_nodes_from([A for A in raw_nodes.nodes()])
    # Now start drawing:
    f = pylab.figure()
    pos=networkx.graphviz_layout(an,prog="neato")
    # draw nodes
    colors = ['yellowgreen', 'saddlebrown', 'slateblue', 'chartreuse']
    for g in [rn,sn,bn]:
        networkx.draw_networkx_nodes(g,pos,node_size=600,
            node_color = colors.pop(), vmin=0.0, vmax = 1.0,alpha = 0.8)
    networkx.draw_networkx_labels(an,pos,font_size = 8)
    # draw edges of different thickness
    networkx.draw_networkx_edges(an,pos,width=2)
    # draw labels
    pylab.xticks([])
    pylab.yticks([])
    f.suptitle('%s Predictions (%s total)'%(title,len(an.nodes())))
    return f


def network_effects(net,title,names={},logodds_cutoff=0.,prog='neato',pos=None,singlesperrow=18):
    """
    Draws a nice graph of all the genes with positive logodds for the relevant disease.
    @param net: A Bayesnet object.
    @param title: Titles of the graphs. Will be preappended with Leery and Naive.
    @param names: Dictionary from the entrez gene ids used in the net to other names.
    @param logodds_cutoff: Cutoff for logodds score needed to be drawn.
    @return: Handles to the two figures.
    """
    import networkx
    import pylab
    all_nodes = networkx.Graph()
    edges = net.edges([node for node in net.nodes() if net.snps[node][1] > logodds_cutoff],data=True)
    all_nodes.add_edges_from([(A,B,float(s)) for (A,B,s) in edges])
    # Remove stuff not in the candidate set.
    for node in all_nodes.nodes():
        try:
            if net.snps[node][1] < logodds_cutoff:
                all_nodes.delete_node(node)
        except:
            pass
    all_nodes.size = {}
    all_nodes.col = {}
    singletons = networkx.Graph()
    for node in all_nodes.nodes():
        try:
            if len(all_nodes.edges(node))==0:
                singletons.add_node(node)
                #all_nodes.delete_node(node)
        except:
            pass
    singles=[v for n,v in sorted([(net.snps[v][1],v) for v in singletons],reverse=True)]
    edges = all_nodes.edges()
    snps=dict([(v,net.snps[v]) for v in all_nodes])
    # Trix with the names.
    labels = {}
    for node in all_nodes.nodes():
        try:
            if names[node]=='':
                labels[node]=node
            else:
                labels[node]=names[node]
        except KeyError:
            labels[node]=node
    # Now start drawing:
    #f = pylab.figure(facecolor='slategrey')
    #pylab.subplot(111, axisbg='slategrey')
    f = pylab.figure()
    if pos is None:
        pos=networkx.graphviz_layout(all_nodes,prog=prog)
        for i,s in enumerate(singles):
            pos[s]=(90+40*(i%singlesperrow),820-80*(i//singlesperrow)-40*(i%2))
    retpos=pos
    legend=networkx.Graph()
    legend.add_node(0)
    for i in range(3):
        all_nodes.add_node(i)
        pos[i]=(810.,270.-80*i)
        snps[i]=(logodds_cutoff+2*i,logodds_cutoff+2*i,0,0)
        labels[i]=str(logodds_cutoff+2*i)
        sizenode="+%s"%(.5*i)
        all_nodes.add_node(sizenode)
        pos[sizenode]=(730.,270.-80*i)
        snps[sizenode]=(2+logodds_cutoff-.5*i,2+logodds_cutoff,0,0)
        labels[sizenode]=str(sizenode)
    #pos=networkx.graphviz_layout(all_nodes,prog="twopi",root=6934)
    # draw nodes
    # colors = [pylab.cm.hot(net.snps[v][1]-net.snps[v][0]) for v in all_nodes]
    colors = [(a,b,c,.8) for (a,b,c,d) in pylab.cm.Oranges([snps[v][1]-snps[v][0] for v in all_nodes])]
    networkx.draw_networkx_nodes(all_nodes,pos,
        node_size=[400*pylab.sqrt(1-logodds_cutoff+snps[v][1]) for v in all_nodes],
        node_color=colors, vmin=0.0, vmax = 1.0,alpha = 1.0)
    networkx.draw_networkx_labels(all_nodes,pos,labels=labels,font_size = 4,font_color='k')
    # draw edges of different thickness
    #networkx.draw_networkx_edges(all_nodes,pos,width=10,alpha=.1)
    networkx.draw_networkx_edges(all_nodes,pos,width=1,alpha=1.)
    # draw labels
    networkx.draw_networkx_labels(legend,{0:(775.,320.)},labels={0:'Legend'},font_size = 8,font_color='k',font_weight='bold')
    pylab.xticks([])
    pylab.yticks([])
    f.suptitle('%s Predictions (%s total)'%(title,len(all_nodes.nodes())-6))
    return f,all_nodes,retpos,singletons

def network_javascript(net,names={},logodds_cutoff=0.,outfile='test.js'):
    """
    Draws a nice graph of all the genes with positive logodds for the relevant disease.
    @param net: A Bayesnet object.
    @param title: Titles of the graphs. Will be preappended with Leery and Naive.
    @param names: Dictionary from the entrez gene ids used in the net to other names.
    @param logodds_cutoff: Cutoff for logodds score needed to be drawn.
    @return: Handles to the two figures.
    """
    import networkx
    import pylab
    all_nodes = networkx.Graph()
    edges = net.edges([node for node in net.nodes() if net.snps[node][1] > logodds_cutoff],data=True)
    all_nodes.add_edges_from([(A,B,float(s)) for (A,B,s) in edges if net.snps[A][2]+net.snps[B][2]>0.])
    # Remove stuff not in the candidate set.
    for node in all_nodes.nodes():
        try:
            if net.snps[node][1] < logodds_cutoff:
                all_nodes.delete_node(node)
        except:
            pass
    all_nodes.size = {}
    all_nodes.col = {}
    edges = all_nodes.edges()
    # Trix with the names.
    labels = {}
    for node in all_nodes.nodes():
        try:
            if names[node]=='':
                labels[node]=node
            else:
                labels[node]=names[node]
        except KeyError:
            labels[node]=node
    outf=open(outfile,'w')
    print >> outf, 'var genenet = {'
    print >> outf, '  nodes:['
    node2number={}
    for number,node in enumerate(all_nodes.nodes()):
        print >> outf, '    {nodeName:"%s", size:%s,color:%s},'%(names[node],net.snps[node][1],pylab.randint(0,15))
        node2number[node]=number
    print >> outf, '  ],'
    print >> outf, '  links:['
    for (A,B,s) in all_nodes.edges(data=True):
        print >> outf, '    {source:%s, target:%s, value:%s},'%(node2number[A],node2number[B],5*pylab.exp(s)*net.snps[A][2])
        print >> outf, '    {source:%s, target:%s, value:%s},'%(node2number[B],node2number[A],5*pylab.exp(s)*net.snps[B][2])
    print >> outf, '  ]'
    print >> outf, '};'
    # Now start drawing:
    #f = pylab.figure(facecolor='slategrey')
    #pylab.subplot(111, axisbg='slategrey')
    f = pylab.figure()
    #pos=networkx.graphviz_layout(all_nodes,prog="fdp")
    pos=networkx.graphviz_layout(all_nodes,prog="circo")
    #pos=networkx.graphviz_layout(all_nodes,prog="twopi",root=6934)
    # draw nodes
    # colors = [pylab.cm.hot(net.snps[v][1]-net.snps[v][0]) for v in all_nodes]
    colors = ['yellowgreen', 'saddlebrown', 'slateblue', 'chartreuse']
    networkx.draw_networkx_nodes(all_nodes,pos,
        node_size=[700*pylab.sqrt(1-logodds_cutoff+net.snps[v][1]) for v in all_nodes],
        node_color=[pylab.cm.Reds(net.snps[v][1]-net.snps[v][0]) for v in all_nodes], vmin=0.0, vmax = 1.0,alpha = 0.9)
    networkx.draw_networkx_labels(all_nodes,pos,labels=labels,font_size = 9,font_color='k')
    # draw edges of different thickness
    networkx.draw_networkx_edges(all_nodes,pos,width=2)
    # draw labels
    pylab.xticks([])
    pylab.yticks([])
    return f,all_nodes

def network_nexus(net,title,names={},logodds_cutoff=0.,boost_cutoff=1.):
    """
    Draws a nice graph of all the genes with positive logodds for the relevant disease.
    @param net: A Bayesnet object.
    @param title: Titles of the graphs. Will be preappended with Leery and Naive.
    @param names: Dictionary from the entrez gene ids used in the net to other names.
    @param logodds_cutoff: Cutoff for logodds score needed to be drawn.
    @param boost_cutoff: Cutoff for logodds improvement needed to be drawn.
    @return: Handles to the two figures.
    """
    import networkx
    import pylab
    all_nodes = networkx.XGraph()
    edges = net.edges([node for node in net.nodes() if net.snps[node][1] > logodds_cutoff])
    all_nodes.add_edges_from([(A,B,float(s)) for (A,B,s) in edges])
    edges = net.edges([node for node in net.nodes() if (net.snps[node][1]-net.snps[node][0]) > boost_cutoff])
    all_nodes.add_edges_from([(A,B,float(s)) for (A,B,s) in edges])
    # Remove stuff not in the candidate set.
    for node in all_nodes.nodes():
        try:
            if net.snps[node][0] < logodds_cutoff and (net.snps[node][1]-net.snps[node][0]) <= boost_cutoff:
                all_nodes.delete_node(node)
        except:
            raise
    all_nodes.size = {}
    all_nodes.col = {}
    dodds_hits = [] # Things that make both cutoffs
    lodds_hits = [] # Things that only make the logodds cutoff
    bodds_hits = [] # Things that only make the boost cutoff
    for node in all_nodes.nodes():
        try:
            if len(all_nodes.edges(node))==0:
                all_nodes.delete_node(node)
            elif net.snps[node][0] >= logodds_cutoff and net.snps[node][1]-net.snps[node][0] >= boost_cutoff:
                dodds_hits.append(node)
            elif net.snps[node][0] >= logodds_cutoff:
                lodds_hits.append(node)
            elif net.snps[node][1]-net.snps[node][0] >= boost_cutoff:
                bodds_hits.append(node)
            else:
                raise Error
        except:
            raise
            #pass
    edges = all_nodes.edges()
    # Trix with the names.
    labels = {}
    for node in all_nodes.nodes():
        try:
            if names[node]=='':
                labels[node]=node
            else:
                labels[node]=names[node]
        except KeyError:
            labels[node]=node
    # Now start drawing:
    #f = pylab.figure(facecolor='slategrey')
    #pylab.subplot(111, axisbg='slategrey')
    for node in bodds_hits:
        print '%s: %s\t%s' %(labels[node],net.snps[node][1]-net.snps[node][0],net.snps[node][0])
    f = pylab.figure()
    #pos=networkx.graphviz_layout(all_nodes,prog="fdp")
    pos=networkx.graphviz_layout(all_nodes,prog="neato")
    #pos=networkx.graphviz_layout(all_nodes,prog="twopi",root=6934)
    # draw nodes
    # colors = [pylab.cm.hot(net.snps[v][1]-net.snps[v][0]) for v in all_nodes]
    colors = dict([(v,pylab.cm.Blues(net.snps[v][1]-net.snps[v][0])) for v in all_nodes.nodes()])
    print len(pos)
    networkx.draw_networkx_nodes(all_nodes,pos,nodelist=dodds_hits,
        node_size=[1000*pylab.sqrt(1-logodds_cutoff+net.snps[v][0]) for v in lodds_hits],node_shape='h',
        node_color=[colors[v] for v in dodds_hits], vmin=0.0, vmax = 1.0,alpha = 0.9)
    networkx.draw_networkx_nodes(all_nodes,pos,nodelist=lodds_hits,
        node_size=[1000*pylab.sqrt(1-logodds_cutoff+net.snps[v][0]) for v in lodds_hits],
        node_color=[colors[v] for v in lodds_hits], vmin=0.0, vmax = 1.0,alpha = 0.9)
    networkx.draw_networkx_nodes(all_nodes,pos,nodelist=bodds_hits,node_size=1000,node_shape='d',
        node_color=[colors[v] for v in bodds_hits],
        vmin=0.0, vmax = 1.0,alpha = 0.9)
    networkx.draw_networkx_labels(all_nodes,pos,labels=labels,font_size = 9,font_color='r')
    # draw edges of different thickness
    networkx.draw_networkx_edges(all_nodes,pos,width=2)
    # draw labels
    pylab.xticks([])
    pylab.yticks([])
    f.suptitle('%s Predictions (%s total)'%(title,len(all_nodes.nodes())))
    return f,all_nodes


def table_maker(net,number_of_candidates):
    """
    Prints a table with the candidates.
    @param net: The bayesnet object used.
    @param number_of_candidates: How many candidates to look at.
    """
    results_ante = [(net.snps[n][0],n) for n in net.nodes()]
    results_ante.sort(reverse=True)
    order_ante = [(results_ante[i][1],i) for i in range(len(results_ante))]
    oa = dict(order_ante)
    results_post = [(net.snps[n][1],n) for n in net.nodes()]
    results_post.sort(reverse=True)
    order_post = [(results_post[i][1],i) for i in range(len(results_post))]
    op = dict(order_post)
    names = name_dict('omim/mart_export.txt')
    class nbrs:
        def __init__(self,l):
            dummylist = [(net.snps[n][1],n) for n in l]
            dummylist.sort(reverse=True)
            self.nbrs = [n[1] for n in dummylist]
        def __str__(self):
            if len(self.nbrs) == 1:
                return names[self.nbrs[0]]
            else:
                return ", ".join([names[n] for n in self.nbrs])
    for (n,o) in order_post[0:number_of_candidates]:
        if net.snps[n][0] != net.snps[n][1]:
            print "%s & %s & %s & %.4f & %s \\\\" %(names[n],op[n],oa[n],net.snps[n][1]-net.snps[n][0],nbrs([B for (A,B,s) in net.edges(n) if net.snps[B][0]>0]))


def name_dict(fname):
    """
    Translates from entrez geneids to real names, using a file downloaded from biomart (via ensambl).
    @param fname: Name of file with geneids.
    @return: Dictionary of names.
    """
    file = open(fname)
    file.readline()
    rows = (row.split('\t') for row in file if row.split('\t')[1] != '')
    ret = {}
    for row in rows:
        ret[int(row[1])]=row[0].strip()
    return ret
    
def name_dict_genenames(fname):
    """
    Translates from entrez geneids to real names, using a file downloaded from biomart (via ensambl).
    @param fname: Name of file with geneids.
    @return: Dictionary of names.
    """
    file = open(fname)
    file.readline()
    rows = (row.split('\t') for row in file)
    ret = {}
    for row in rows:
        try:
            ret[int(row[10])]=row[1].strip()
        except ValueError:
            pass
    return ret
    

def candidates(net,names,col=3):
    """
    Returns a ranked list of all the candidates.
    @param net: A bayesnet with the disease.
    @param names: A dictionary with all the names.
    @return: A ranked list of all the candidates.
    """
    if col == 3:
        cands = [(net.snps[gene][1]-net.snps[gene][0],gene) for gene in net]
    else:
        cands = [(net.snps[gene][col],gene) for gene in net]
    cands.sort(reverse=True)
    for gene in net:
        try:
            x = names[gene]
        except KeyError:
            names[gene]=gene
    return [(names[g[1]],g[1],net.snps[g[1]][0],g[0]) for g in cands]
    
