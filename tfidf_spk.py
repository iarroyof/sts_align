# This is a tfIDF vectorizer using pySpark.
# Documentation examples were followed.
# Spark installation process: (https://askubuntu.com/questions/635265/how-do-i-\
# get-pyspark-on-ubuntu)
#
# 1. Download Spark from https://spark.apache.org/downloads.html
# 2. Unzip and move the unzipped directory to a working directory:
#
#        $ tar -xzf spark-<version>-bin-hadoop2.6.tgz
#
#        $ mv spark-<version>-bin-hadoop2.6 /work_directory/spark-<version>
#
# 3. Symlink the version of Spark to a spark directory:
#
#        $ ln -s /work_directory/spark-<version> /work_directory/spark

# 4. Edit ~/.bashrc using your favorite text editor and add Spark to your PATH
#    and set the SPARK_HOME environment variable:
#
#        export SPARK_HOME=/work_directory/spark
#        export PATH=$SPARK_HOME/bin:$PATH
#        export PYTHONPATH=$SPARK_HOME/python:$SPARK_HOME/python/build:$PYTHONPATH
#       $ . ~/.bashrc
# 5. Install py4j via pip:
#
#       $ sudo pip install py4j
#
# Now you should be able to execute pyspark by running the command pyspark in
# the terminal as well as from python programs.

from pyspark.ml.feature import RegexTokenizer
from pyspark.ml.feature import IDF, IDFModel
from pyspark.ml.feature import CountVectorizer
from pyspark.sql import SparkSession
from os.path import dirname
import argparse

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="""Input file containing openIE triplets
                                            of a sentence.""", default=None)
    parser.add_argument("--predict", help="""Toggles predicting mode from --input
                                            given a pre-trained tfidf model
                                            (--model).""", action="store_true")
    parser.add_argument("--model", help="Output/input folder model container.",
                                                            default=None)
    args = parser.parse_args()
    # Spark Config
    spark = SparkSession.builder.getOrCreate()
    sc = spark.sparkContext

    text_file=args.input
    if  not args.model:
        tfidf_dir=dirname(text_file)+"/tfidf_model"
    else:
        tfidf_dir=args.model

    documents = sc.textFile(text_file)
    docsDataFrame = spark.createDataFrame([(id, doc)
                                for id, doc in enumerate(documents.collect())],
                                ["id", "docs"])
    regexTokenizer = RegexTokenizer(inputCol="docs", outputCol="words", pattern="\\W")
    tokenized = regexTokenizer.transform(docsDataFrame)

    cv = CountVectorizer(inputCol="words", outputCol="tf", minDF=2.0)
    cvTF=cv.fit(tokenized)
    tf=cvTF.transform(tokenized)

    if not args.predict:
        idf = IDF(inputCol="tf", outputCol="idf")
        idfModel = idf.fit(tf)
        tfidfData = idfModel.transform(tf)
        idfModel.save(tfidf_dir)
        print "The saved model:"
        print tfidfData.show()
    else:
        loadedModel = IDFModel.load(tfidf_dir)
        pred_idf_df = loadedModel.transform(tf)
        pred_idf_df.show()

    spark.stop()
