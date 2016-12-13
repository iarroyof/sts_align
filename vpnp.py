import csv
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-i", help="Input tab separated parsing (conll format).", metavar="input_file", required=True)
parser.add_argument("-d", help="When required, specify directory of the file of Penn tags.", metavar="tag_dir", default="")
#parser.add_argument("-v", action='store_true', default=False, dest = "verbose", help="Toggles if you want Verbose logs in the output.")
args = parser.parse_args()

verbs=[]
nouns=[]
verb_tags = []
noun_tags = []
othe_tags = []
penn_tags = args.d + "penntb.g"

with open(penn_tags, 'r') as f:
    lines = f.readlines()
    for line in lines:
        tl = line.split(" - ")
        
        if "verb" in tl[1]:
            verb_tags.append(tl[0])
        elif "noun" in tl[1]:
            noun_tags.append(tl[0])
        else:
            othe_tags.append(tl[0])
                
with open(args.i, 'rU') as f:  #opens parsed Conll format tags file
    data = list(list(rec) for rec in csv.reader(f, delimiter='\t')) #reads csv into a list of lists
    
    for sublist in data:
        filt = filter(lambda x: x in verb_tags, [w.lower() for w in sublist])
        if filt:
            #verbs.append((sublist[1], filt[0]))
            verbs.append(sublist[1])
            continue
        filt = filter(lambda x: x in noun_tags, [w.lower() for w in sublist])
        
        if filt:
            nouns.append(sublist[1])

vp = "VP\t"
for w in verbs:
    vp = vp + w + "\t"
vp = vp[:-1] + "\n"

np = "NP\t"
for w in nouns:
    np = np + w + "\t"
np = np[:-1] + "\n"

print(np + vp)
