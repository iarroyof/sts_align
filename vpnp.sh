sent_file=$1
java -cp "$ST/*" -Xmx2g edu.stanford.nlp.pipeline.StanfordCoreNLP -annotators tokenize,ssplit,pos -outputFormat conll -file "$sent_file" -outputDirectory $(dirname "$sent_file")
python vpnp.py -i "$sent_file".conll
