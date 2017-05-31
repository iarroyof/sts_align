#!/usr/bin/python
# -*- coding: latin-1 -*-
from gensim.models.keyedvectors import KeyedVectors as vDB
load_vectors=vDB.load_word2vec_format
from w2v import *
from itertools import product
from numpy import mean, multiply, array, cumsum, insert
import argparse
import cPickle as pickle
from sklearn.metrics.pairwise import cosine_distances, euclidean_distances, manhattan_distances
import logging
import spectral


from pdb import set_trace as st


logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                    level=logging.INFO)

class streamer(object):
    def __init__(self, file_name):
        self.file_name=file_name

    def __iter__(self):
        for s in open(self.file_name):
            yield s.strip()

def running_mean(x, N=4):
    ac = cumsum(insert(x, 0, 0.0, axis=0), axis=0) 
    return (ac[N:] - ac[:-N]) / N

def infer_tfidf_weights(sentence, vectorizer, predict=False):
    existent={}
    missing=[]

    if not vectorizer:
        for word in sentence.split():
            existent[word]=1.0

        return existent, missing

    if predict:
        unseen=vectorizer.transform([sentence]).toarray()
        for word in sentence.split():
            try:
                existent[word]=unseen[0][vectorizer.vocabulary_[word]]
            except KeyError:
                missing.append(word)
                continue

    else:
        for word in sentence.split():
            try:
                weight=vectorizer.idf_[vectorizer.vocabulary_[word]]
                existent[word]=weight if weight > 2 else 0.01
            except KeyError:
                missing.append(word)
                continue

    return existent, missing

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--tfidf", help="""Input file containing TFIDF pre-trained
                                            weights. If not provided, all weights
                                            will be 1.0 (pickled sklearn object).""",
                                            default=None)
    parser.add_argument("--embed", help="""Input file containing word embeddings
                                            model (extension says me file type:
                                            binary or text).""", required=True)
    parser.add_argument("--pairs", help="""Input file containing tab-separated
                                            sentence pairs.""", required=True)
    parser.add_argument("--dist", help="""Desired distance to compute between
                                            resulting vector pairs. {cos, euc, man, 
                                            all}""", default="cos")
    parser.add_argument("--rwin", help="""Size (integer) of the running average 
                                            window.""", default=3, type=int)
    parser.add_argument("--comb", help="""Desired word vector combination for
                                            sentence representation {sum, moving, 
                                            avg}.""", default="sum")
    parser.add_argument("--suffix", help="A suffix to add to the output file",
                                            default="")
    parser.add_argument("--pi_tfidf", help="""To predict TFIDF weights (pred) or 
                                            to get them directly from prefitted 
                                            model (infe) or to set all equal to 
                                            1.0 (1).""", default=None)
    parser.add_argument("--ortho", help="""To orthogonalize word vectors by using 
                                           The Gram–Schmidt process (ortho). (ld) 
                                           keeps original word vectors.""", 
                                           default=None) 
    args = parser.parse_args()
    # '/almac/ignacio/data/INEXQA2012corpus/wikiEn_sts_clean_ph2_tfidf.pk'
    pairs=streamer(args.pairs)

    if args.pi_tfidf.startswith("pred"):
        pred_tfidf=True
    elif args.pi_tfidf.startswith("infe"):
        pred_tfidf=False
    elif args.pi_tfidf.startswith("1"):
        pred_tfidf=False
        tfidf=False

    if args.comb.startswith("sum"):
        average=False
    elif args.comb.startswith("moving"):
        average="moving"
        rmean_win=args.rwin
    elif args.comb.startswith("avg"):
        average="whole"

    if args.tfidf!=None and not args.pi_tfidf.startswith("1"):
        logging.info("Loading TFIDF weights from: %s ..." % args.tfidf)
        tfidf=pickle.load(open(args.tfidf, 'rb'))
    else:
        tfidf=False

    embedding=load_vectors(args.embed, binary=False, encoding="latin-1")
    # TODO: In the case this approach to work, try other pairwise metrics (sklearn)
    embedding_name=args.embed #"_".join(args.embed.split("/")[-1].split(".")[:-1])
    suffix= "_".join([embedding_name, args.ortho, args.comb, args.pi_tfidf, args.suffix]).strip("_")

    distances=[]
    missing_bow=[]
    missing_cbow=[]
    for pair in pairs:
        p=pair.split("\t")
        weights_a, m=infer_tfidf_weights(' '.join(clean_Ustring_fromU(p[0])), tfidf, predict=pred_tfidf)
        missing_bow+= [m] if isinstance(m, list) else m
        weights_b, m=infer_tfidf_weights(' '.join(clean_Ustring_fromU(p[1])), tfidf, predict=pred_tfidf)
        missing_bow+=[m] if isinstance(m, list) else m
        for w in weights_a:
            try:
                weights_a[w]=(weights_a[w], embedding[w])
            except KeyError:
                weights_a[w]=0
                missing_cbow.append(w)
                continue
        logging.info("Weights sentence A %s" % [(w, weights_a[w][0]) for w in weights_a if not weights_a[w] is 0])

        for w in weights_b:
            try:
                weights_b[w]=(weights_b[w], embedding[w])
            except KeyError:
                weights_b[w]=0
                missing_cbow.append(w)
                continue
        logging.info("Weights sentence B %s" % [(w, weights_b[w][0]) for w in weights_b if not weights_b[w] is 0])

        if not average:
            if args.ortho.startswith("ld"):
                v_a=array([weights_a[w][0]*weights_a[w][1] 
                                  for w in weights_a if weights_a[w]!=0]).sum(axis=0).reshape(1, -1)
                v_b=array([weights_b[w][0]*weights_b[w][1] 
                                  for w in weights_b if weights_b[w]!=0]).sum(axis=0).reshape(1, -1)
            elif args.ortho.startswith("orth"):
                v_a=spectral.orthogonalize(array([weights_a[w][1] for w in weights_a if weights_a[w]!=0]))
                w_a=array([weights_a[w][0] for w in weights_a if weights_a[w]!=0])
                v_a=multiply(v_a.T, w_a).T.sum(axis=0).reshape(1, -1)
                v_b=spectral.orthogonalize(array([weights_b[w][1] for w in weights_b if weights_b[w]!=0]))
                w_b=array([weights_b[w][0] for w in weights_b if weights_b[w]!=0])
                v_b=multiply(v_b.T, w_b).T.sum(axis=0).reshape(1, -1)
        elif average.startswith("moving"):
            if args.ortho.startswith("ld"):
                v_a=array([weights_a[w][1] for w in weights_a if weights_a[w]!=0])
                v_a=running_mean(v_a, rmean_win).sum(axis=0).reshape(1, -1)
                v_b=array([weights_b[w][1] for w in weights_b if weights_b[w]!=0])
                v_b=running_mean(v_b, rmean_win).sum(axis=0).reshape(1, -1)
            elif args.ortho.startswith("orth"):
                v_a=array([weights_a[w][1] for w in weights_a if weights_a[w]!=0])
                v_a=running_mean(spectral.orthogonalize(v_a), rmean_win).sum(axis=0).reshape(1, -1)
                v_b=array([weights_b[w][1] for w in weights_b if weights_b[w]!=0])
                v_b=running_mean(spectral.orthogonalize(v_b), rmean_win).sum(axis=0).reshape(1, -1)
        elif average.startswith("whole"):
            if args.ortho.startswith("ld"):
                v_a=array([weights_a[w][1] for w in weights_a if weights_a[w]!=0])
                v_a=v_a.mean(axis=0).reshape(1, -1)
                v_b=array([weights_b[w][1] for w in weights_b if weights_b[w]!=0])
                v_b=v_b.mean(axis=0).reshape(1, -1)
            elif args.ortho.startswith("orth"):
                v_a=array([weights_a[w][1] for w in weights_a if weights_a[w]!=0])
                v_a=spectral.orthogonalize(v_a).mean(axis=0).reshape(1, -1)
                v_b=array([weights_b[w][1] for w in weights_b if weights_b[w]!=0])
                v_b=spectral.orthogonalize(v_b).mean(axis=0).reshape(1, -1)
        #v_a=array([weights_a[word]*embedding[word]
        #                                    for word in weights_a]).sum(axis=0).reshape(1, -1)
        #v_b=array([weights_b[word]*embedding[word]
        #                                    for word in weights_b]).sum(axis=0).reshape(1, -1)
        if args.dist.startswith("all"):
            distances.append((1-cosine_distances(v_a, v_b), 
                                euclidean_distances(v_a, v_b),
                                manhattan_distances(v_a, v_b)))
        elif args.dist.startswith("euc"):
            distances.append(euclidean_distances(v_a, v_b))
        elif args.dist.startswith("cos"):
            distances.append(cosine_distances(v_a, v_b))
        elif args.dist.startswith("man"):
            distances.append(manhattan_distances(v_a, v_b))

    with open(args.pairs+".output_"+suffix, "w") as f:
        if args.dist.startswith("all"):
            for item in distances:
                f.write("%f\t%f\t%f\n" % (item[0][0], item[1][0], item[2][0]))
        else:
            for item in distances:
                f.write("%f\n" % item[0])
    # Print missing words for the given pretrained model
    if not os.path.isfile(args.pairs+".missing_"+ embedding_name):
        with open(args.pairs+".missing_"+ embedding_name, "w") as f:
            f.write("%s\n" % {"bow": missing_bow, "cbow": missing_cbow})

    logging.info("FINISHED and writing results to: %s" % args.pairs+".output_"+suffix)
