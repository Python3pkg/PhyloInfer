import matplotlib.pyplot as plt
import numpy as np
import re
from Bio import Phylo
from io import StringIO
from .treeManipulation import init
from phyloinfer import Tree
from collections import defaultdict



def treeStats(sampled_tree, target_tree_dict=None):
    if not target_tree_dict:
        id2stats = defaultdict(int)
        id2tree = defaultdict()
        for tree in sampled_tree:
            ID = tree.get_topology_id()
            id2stats[ID] += 1
            if ID not in id2tree:
                id2tree[ID] = tree

    else:
        id2stats = {tree.get_topology_id():0.0 for _,tree in list(target_tree_dict.items())}
        id2tree = {tree.get_topology_id():_ for _,tree in list(target_tree_dict.items())}
        for tree in sampled_tree:
            ID = tree.get_topology_id()
            if ID in id2stats:
                id2stats[ID] += 1     

    tree_samp_count = len(sampled_tree)*1.0
    for tree_id in id2stats:
        id2stats[tree_id] /= tree_samp_count
    return sorted(list(id2stats.items()), key=lambda x:x[1], reverse=True), id2tree


def savePara(sampled_branch, filename, ID):
    branch_count = len(sampled_branch[0])
    with open(filename,'w') as output_file:
        output_file.write('[ID:{}]\n'.format(ID))
        output_file.write('nIter' + '\t' + '\t'.join(['length[{}]'.format(i) for i in range(branch_count)]) + '\n')
        for i, branch in enumerate(sampled_branch):
            output_file.write(str(i) + '\t' + '\t'.join([str(branch) for branch in sampled_branch[i]]) + '\n')

            
def readPara(filename):
    with open(filename,'r') as readin_file:
        id_line = readin_file.readline()
        ID = ''.join(re.split('\[|\]|ID:',id_line)).strip()
        name_line = readin_file.readline()
        names = name_line.strip('\n').split('\t')
        stats_dict = {name:[] for name in names}
        
        while True:
            line = readin_file.readline()
            if line == "": 
                break
            for i, stats in enumerate(line.strip('\n').split('\t')):
                stats_dict[names[i]].append(float(stats))
            
    return stats_dict, names, ID 


def saveTree(sampled_tree, filename, tree_format, ID):
    if type(sampled_tree) is not list:
        sampled_tree = [sampled_tree]
        
    with open(filename,'w') as output_file:
        output_file.write('[ID:{}]\n'.format(ID))
        for i, tree in enumerate(sampled_tree):
            tree_newick = tree.write(format=tree_format)
            output_file.write('tree_{}'.format(i) + '\t' + tree_newick + '\n')
            

def readTree(filename, tree_format=3):
    with open(filename,'r') as readin_file:
        id_line = readin_file.readline()
        ID = ''.join(re.split('\[|\]|ID:',id_line)).strip()
        samp_tree_list = []
        while True:
            line = readin_file.readline()
            if line == "":
                break
            tree_name, newick = line.strip('\n').split('\t')
            samp_tree_list.append(Tree(newick,format=tree_format))
            init(samp_tree_list[-1], name='interior')
        
    return samp_tree_list


def mcmc_treeprob(filename, data_type, truncate=10):
    mcmc_samp_tree_stats = Phylo.parse(filename, data_type)
    mcmc_samp_tree_dict = {}
    mcmc_samp_tree_name = []
    mcmc_samp_tree_wts = []
    num_hp_tree = 0
    for tree in mcmc_samp_tree_stats:
        handle = StringIO()
        Phylo.write(tree, handle,'newick')
        mcmc_samp_tree_dict[tree.name] = Tree(handle.getvalue().strip())
        init(mcmc_samp_tree_dict[tree.name],name='interior')
        handle.close()
        mcmc_samp_tree_name.append(tree.name)
        mcmc_samp_tree_wts.append(tree.weight)
        num_hp_tree += 1
        if num_hp_tree >= truncate: break
    
    return mcmc_samp_tree_dict, mcmc_samp_tree_name, mcmc_samp_tree_wts
    
        