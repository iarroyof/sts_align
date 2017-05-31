pair=$1 # File of pairs dataset
gs=$2   # File of labels associated to pairs
c=$3
r=$4

printf "Embedding Size Transform Combine TFIDF Cosine Euclidean Manhattan\n" > all_results
export LC_NUMERIC="en_US.UTF-8"
paste <(for r in `ls "$pair".output*`; do printf "%s\\t%s\\t%f\\n" "${r##*output_}" $(perl $NLP/correlation-noconfidence.pl "$gs" <(awk -F '\\t' '{print match($1, /[^ ]/) ? $1 : "0.1"}' "$r")); done) <(for r in `ls "$pair".output*`; do printf "%s\\t%s\\t%f\\n" "${r##*output_}" $(perl $NLP/correlation-noconfidence.pl "$gs" <(awk -F '\\t' '{print match($2, /[^ ]/) ? $2 : "0.1"}' "$r")); done) <(for r in `ls "$pair".output*`; do printf "%s\\t%s\\t%f\\n" "${r##*output_}" $(perl $NLP/correlation-noconfidence.pl "$gs" <(awk -F '\\t' '{print match($3, /[^ ]/) ? $3 : "0.1"}' "$r")); done) | awk '{ print $1, $3, $6, $9 }' >> all_results
#cat all_results|sed 's/^-\(.*\)/\1-/'

if [ ! -z "$c" ]; then
    if [ ! -z "$r" ]; then
        cat all_results |perl -i -pe 's/ -/ /g' | perl -i -pe 's/_/ /g'| sort -nrk "$c"
	#cat all_results | sort -nrk "$c"
    else
        cat all_results |perl -i -pe 's/ -/ /g' | perl -i -pe 's/_/ /g'| sort -nk "$c"
        #cat all_results | sort -nk "$c"
    fi
else
    cat all_results|perl -i -pe 's/ -/ /g'|head
fi
