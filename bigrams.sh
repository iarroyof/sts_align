#tokenise words
cat "$1" | tr -d '[:punct:]' | perl tokenize.pl > out1
#create 2nd list offset by 1 word
tail -n+2 out1 > out2
#paste list together
paste out1 out2 | gawk -i inplace '{gsub("\t"," ")}1'
#clean up
rm out1 out2
