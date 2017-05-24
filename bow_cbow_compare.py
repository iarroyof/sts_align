
from gensim.models.keyedvectors import KeyedVectors as vDB
load_vectors=vDB.load_word2vec_format
from numpy import mean, median, array, sum
import cPickle as pickle
from sklearn.metrics.pairwise import cosine_distances, euclidean_distances


class streamer(object):
    def __init__(self, file_name):
        self.file_name=file_name

    def __iter__(self):
        for s in open(self.file_name):
            yield s.strip()

def infer_tfidf_weights(sentence, vectorizer, predict=False):
    existent={}
    if predict:
        unseen=vectorizer.transform(sentence)
        for word in sentence.split():
            existent[word]=unseen[vectorizer.vocabulary_[word]]
        return existent
    else:
        for word in sentence.split():
            existent[word]=vectorizer.idf_[vectorizer.vocabulary_[word]]
        return existent

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--tfidf", help="""Input file containing TFIDF pre-trained
                                            weights (pickled sklearn object).""",
                                            required=True)
    parser.add_argument("--embed", help="""Input file containing word embeddings
                                            model (extension says me file type:
                                            binary or text).""", required=True)
    parser.add_argument("--pairs", help="""Input file containing tab-separated
                                            sentence pairs.""", required=True)
    parser.add_argument("--dist", help="""Desired distance to compute between
                                            resulting vector pairs. {cos, euc}""",
                                            default="cos")
    parser.add_argument("--pred_tfidf", help="""Toggles whether to predict TFIDF
                                            weights or to get them directly from
                                            prefitted model.""", action="store_true")
    args = parser.parse_args()
    # '/almac/ignacio/data/INEXQA2012corpus/wikiEn_sts_clean_ph2_tfidf.pk'

    pairs=streamer(args.pairs)
    tfidf=pickle.load(open(args.tfidf, 'rb'))
    embedding=load_vectors(args.embed, binary=False, encoding="latin-1")
    # TODO: In the case this approach to work, try other pairwise metrics (sklearn)
    #distance={"cos": cosine_distances, "euc": euclidean_distances}

    distances=[]
    for pair in pairs:
        p=pair.split("\t")
        weights_a=infer_tfidf_weights(p[0], tfidf, predict=False)
        weights_b=infer_tfidf_weights(p[1], tfidf, predict=False)
        v_a=array([weights_a[word]*embedding[word]
                                            for word in weights_a]).sum(axis=0)
        v_b=array([weights_b[word]*embedding[word]
                                            for word in weights_b]).sum(axis=0)
        if args.startswith("cos"):
            distances.append(1-cosine_distances(v_a, v_b))
        elif args.startswith("euc"):
            distances.append(euclidean_distances(v_a, v_b))

        print distances[-1]
