# Example:

# 1.0 entity  existed in  location
# 1.0 entity  formerly existed in location
# ---------------------------------------------
# an indication that something has been present;

from pdb import set_trace as st
import numpy as np
import array
import string as strg
import argparse
from os.path import dirname, basename
exc = set(strg.punctuation.replace('-',''))

parser = argparse.ArgumentParser()
parser.add_argument("-A", help="Input file name of triplets sentence A (vectos for A and vectors-sentences B must be present in the same directory.)", metavar="input_file_tripA", required=True)
parser.add_argument("-v", action='store_true', default=False, dest = "verbose", help="Toggles if you want Verbose logs in the output.")
args = parser.parse_args()

fA = args.A                                             # input_file_triples sentence A
fa = dirname(fA) + "/" + basename(fA) + ".ftw"          # input_file_vectors sentence A
fB = dirname(fA) + "/" + "b" + basename(fA)[1:]         # input_file_triples sentence B
fb = dirname(fA) + "/" + "b" + basename(fA)[1:] + ".ftw" # input_file_vectors sentence B
comp = "00"

with open(fA, "r") as f: # File containing triplets or NPVP tuples
    lines = f.readlines()
    from re import match
    if match("0\.\d+\\t|1\.0\\t", lines[0]): #lines[0].startswith("1.0\t"):
        trips = []
        comp = '1' + comp[1:]
        with open(fa, "r") as F:
            phr_vects = {line.strip().lower().split()[0]: np.fromstring(" ".join(line.split()[1:]), sep=" ")\
                                                                                             for line in F.readlines()} # phrases and vectors
        for line in lines:        
            trips.append(line.strip().lower().split("\t")[1:]) # get triplets tab apaced rows, all except the initial "1.0"
        try:
            # Get vector of each word/term and put them
            # together into a dictionary anthe into a list
            terms_oieA = [{"NP_" + t[0].replace(' ', '_'): phr_vects[t[0].replace(' ', '_')], \
                           "VP_" + t[1].replace(' ', '_'): phr_vects[t[1].replace(' ', '_')], \
                           "NP_" + t[2].replace(' ', '_'): phr_vects[t[2].replace(' ', '_')] } for t in trips] 
                # [{"nphr_a":vector, "Vphr_1":vector, "n_phr_b":vector},.., {"n_phr_a":vector, "Vphr_N":vector, "n_phr_b":vector}]
        except Exception, e: 
            print basename(fA) + " :: trip :: " + str(e)
            exit()
    elif match("NP\\t", lines[0]):
        comp = '0' + comp[1:]      
        dups = []
        with open(fa, "r") as F:
            vectors = F.readlines() # term_bonito 0.123 3.2134 -2.342
            phr_vects = {line.strip().lower().split()[0]: np.fromstring(" ".join(line.split()[1:]), sep=" ")\
                                                                                             for line in vectors} # phrases and vectors
            try:
                dups.append(lines[0].strip().lower().split("\t")[1:]) # NP term np    term    ... noun
                dups.append(lines[1].strip().lower().split("\t")[1:]) # VP term vp    verb    ... phra

                terms_oieA = []
                terms_oieA.append({"NP_" + t.replace(' ', '_'): phr_vects[t.replace(' ', '_')]  for t in dups[0]}) # get vector of each word/term and put them
                terms_oieA.append({"VP_" + t.replace(' ', '_'): phr_vects[t.replace(' ', '_')]  for t in dups[1]}) # together into a dictionary
                
            except Exception, e: 
                print basename(fA) + " :: sent :: " + str(e)
                exit()

with open(fB, "r") as f:
    lines = f.readlines()
    if match("0\.\d+\\t|1\.0\\t", lines[0]):
        trips = []
        comp = comp[0] + '1' # 01
        with open(fb, "r") as F:
            phr_vects = {line.strip().lower().split()[0]:np.fromstring(" ".join(line.split()[1:]), sep=" ") for line in F.readlines()} # phrases and vectors
        
        for line in lines:        
            trips.append(line.strip().lower().split("\t")[1:]) # all except the initial "1.0"
        try:
            terms_oieB = [{"NP_" + t[0].replace(' ', '_'):phr_vects[t[0].replace(' ', '_')], \
                           "VP_" + t[1].replace(' ', '_'):phr_vects[t[1].replace(' ', '_')], \
                           "NP_" + t[2].replace(' ', '_'): phr_vects[t[2].replace(' ', '_')]} for t in trips] 
        # [{"nphr_a":vector, "Vphr_1":vector, "n_phr_b":vector},.., {"n_phr_a":vector, "Vphr_N":vector, "n_phr_b":vector}]
        except Exception, e:
            print basename(fB) + ": trip :" + str(e)
            exit()
    elif match("NP\\t", lines[0]):
        comp = comp[0] + '0'        
        dups = []
        with open(fb, "r") as F:
            vectors = F.readlines() # term_bonito 0.123 3.2134 -2.342
            phr_vects = {line.strip().lower().split()[0]: np.fromstring(" ".join(line.split()[1:]), sep=" ")\
                                                                                             for line in vectors} # phrases and vectors
            try:
                dups.append(lines[0].strip().lower().split("\t")[1:]) # NP term np    term    ... noun
                dups.append(lines[1].strip().lower().split("\t")[1:]) # VP term vp    verb    ... phra

                terms_oieB = []
                terms_oieB.append({"NP_" + t.replace(' ', '_'): phr_vects[t.replace(' ', '_')]  for t in dups[0]}) # get vector of each word/term and put them
                terms_oieB.append({"VP_" + t.replace(' ', '_'): phr_vects[t.replace(' ', '_')]  for t in dups[1]}) # together into a dictionary

            except Exception, e:
                print basename(fB) + ": sent :" + str(e)
                exit()

from scipy.spatial.distance import cosine
import operator
# Given properties of fastText embeddings, a comparison of cross features is proposed. That is, NPs will be compared 
# against VPs. fastText presented high similarities between co-ordered words/terms rather than between context 
# sharing words/terms.
trip_dist = []

if comp == "10": 
    dist_NVPs = []
    dist_VNPs = []    
    dist = []

    for word in terms_oieB[0]: # (NPs)
    # [{"NP_phrse_1":vector,..., "NP_phrase_m":vector}, {"VP_phrse_1":vector,..., "VP_phrase_m'":vector}]
        for triplet in terms_oieA:
        # [{"nphr_a":vector, "Vphr_1":vector, "n_phr_b":vector},.., {"n_phr_a":vector, "Vphr_N":vector, "n_phr_b":vector}]
            for t in triplet:
                if t.startswith("VP_"):
                    dist.append( cosine(triplet[t], terms_oieB[0][word]) )
                
        dist_NVPs.append(dist) 
        dist = []
    dist_NVPs = np.array(reduce(operator.add, dist_NVPs))
    dist = []
    
    for word in terms_oieB[1]: # (VPs)
        for triplet in terms_oieA:
            for t in triplet :
                if t.startswith("NP_"):
                    dist.append( cosine(triplet[t], terms_oieB[1][word]) )
        dist_VNPs.append(dist)
        dist = []
    dist_VNPs = np.array(reduce(operator.add, dist_VNPs))
    #trip_dist = np.mean(dist_VNPs) + np.mean(dist_NVPs)
    
elif comp == "01":
    dist_NVPs = []
    dist_VNPs = [] 
    dist = []

    for word in terms_oieA[0]: # (NPs)
    # [{"NP_phrse_1":vector,..., "NP_phrase_m":vector}, {"VP_phrse_1":vector,..., "VP_phrase_m'":vector}]
        for triplet in terms_oieB:
        # [{"nphr_a":vector, "Vphr_1":vector, "n_phr_b":vector},.., {"n_phr_a":vector, "Vphr_N":vector, "n_phr_b":vector}]
            dist.append( [cosine(triplet[t], terms_oieA[0][word]) for t in triplet if t.startswith("VP_")] )
        dist_NVPs.append(dist) 
    dist_NVPs = np.array(reduce(operator.add, dist_NVPs))
    dist = []

    for word in terms_oieA[1]: # (VPs)
        for triplet in terms_oieB:
            dist.append( [cosine(triplet[t], terms_oieA[1][word]) for t in triplet if t.startswith("NP_")] )
        dist_VNPs.append(dist)
    dist_VNPs = np.array(reduce(operator.add, dist_VNPs))
    
    #trip_dist = np.mean(dist_VNPs) + np.mean(dist_NVPs)

elif comp == "00": # PoS both A and B
    dist_NVPs = []
    dist_VNPs = []
    # [{"NP_phrse_1":vector,..., "NP_phrase_m":vector}, {"VP_phrse_1":vector,..., "VP_phrase_m'":vector}]
    dist_NVPs.append( [cosine(terms_oieA[0][NP_a], terms_oieB[1][VP_b]) \
                            for NP_a in terms_oieA[0] for VP_b in terms_oieB[1] ] )# (NPs)
    dist_VNPs.append( [cosine(terms_oieA[1][VP_a], terms_oieB[0][NP_b]) \
                            for VP_a in terms_oieA[1] for NP_b in terms_oieB[0] ] ) # (VPs)

elif comp == "11": # Triplets A and B
    dist_NVPs = []
    dist_VNPs = []
    
    for triplet_b in terms_oieB:
        # [{"nphr_a":vector, "Vphr_1":vector, "n_phr_b":vector},.., {"n_phr_a":vector, "Vphr_N":vector, "n_phr_b":vector}]
        for triplet_a in terms_oieA:
            # [{"nphr_a":vector, "Vphr_1":vector, "n_phr_b":vector},.., {"n_phr_a":vector, "Vphr_N":vector, "n_phr_b":vector}]
            for t_a in triplet_a:
                for t_b in triplet_b: 
                    if t_a.startswith("NP_") and t_b.startswith("VP_"):
                        dist_NVPs.append( cosine(triplet_a[t_a], triplet_b[t_b]) )
                    if t_a.startswith("VP_") and t_b.startswith("NP_"):
                        dist_VNPs.append( cosine(triplet_a[t_a], triplet_b[t_b]) )


#-----------------------------------------------------------------------------------------
#if args.v:
#    if args.s:
#        sentences = args.s.strip().split("\t")
#        print ">> Input sentences:>> %s\n%s" % (sentences[0], sentences[1])
#    try:
#        ta = [t.keys() for t in terms_oieA]
#    except:
#        ta = terms_oieA[0]
#    try:
#        tb = [t.keys() for t in terms_oieB]
#    except:
#        tb = terms_oieB[0]
#    print ">> triplets:>> %s\n%s" % (ta, tb)
#    print ">> Distances:>> %s" % trip_dist
#    print ">> Global distance:>> %.5f" % (5.0 * trip_dist)
#else:
#    print "%.5f" % (5.0 * trip_dist)
print "Verbs to Nouns: %s" % dist_VNPs
print "Nouns to verbs: %s" % dist_NVPs

trip_dist = np.median(dist_VNPs) + np.median(dist_NVPs)
print "%.5f" % (trip_dist)
