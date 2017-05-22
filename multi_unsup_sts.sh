yearDir=$1
dSet=$2
dims=$3

bash $USTS/unsup_sts.sh $DATA/sts_all/"$yearDir"/STS.input."$dSet".txt\
 $DATA/fstx_models/wikiEn_Full_H"$dims".model.bin all > \
 $USTS/results/scores_"$dSet"_H"$dims"_"${yearDir:(-4)}"
