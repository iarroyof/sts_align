pair=$1 # File of pairs dataset
gs=$2   # File of labels associated to pairs
c=$3
r=$4

printf "Configuration Cosine Euclidean Manhattan\n" > all_results
paste <(for r in `ls "$pair".output*`; do printf "%s\\t%s\\t%f\\n" "${r##*output_}" $(perl $NLP/correlation-noconfidence.pl "$gs" <(awk -F '\\t' '{print match($1, /[^ ]/) ? $1 : "0.1"}' "$r")); done) <(for r in `ls "$pair".output*`; do printf "%s\\t%s\\t%f\\n" "${r##*output_}" $(perl $NLP/correlation-noconfidence.pl "$gs" <(awk -F '\\t' '{print match($2, /[^ ]/) ? $2 : "0.1"}' "$r")); done) <(for r in `ls "$pair".output*`; do printf "%s\\t%s\\t%f\\n" "${r##*output_}" $(perl $NLP/correlation-noconfidence.pl "$gs" <(awk -F '\\t' '{print match($3, /[^ ]/) ? $3 : "0.1"}' "$r")); done) | awk '{ print $1, $3, $6, $9 }' >> all_results
#cat all_results|sed 's/^-\(.*\)/\1-/' | sort -g|sort -gk "$c"

if [ ! -z "$c" ]; then
    if [ ! -z "$r" ]; then
        sort -nrk "$c" all_results
    else
        sort -nk "$c" all_results
    fi
else
    head all_results
fi
