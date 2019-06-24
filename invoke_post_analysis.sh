
#!/bin/bash
XGC_dirs=`ls | grep "GS"`
GS_dirs=`ls | grep "GS"`
XGC_dirs="EXP13_XGC_GENE_24_4_4_4_1"
exp_dirs="${XGC_dirs}"

for exp_dir in ${exp_dirs}
do
for w1 in 120
do 
    for w2 in 30
    do
        echo "Processing ... ${w1} ${w2} ${exp_dir}"
        python3 bs_filter.py ${w1} ${w2} ${exp_dir}
        #exit
    done

done
#exit
done
