#!/bin/bash

export directory=${1}
export directory1=${1}_images

EXPS_DIR=`ls -l ${directory}| grep ^d | sed -e "s/.* //"`

echo ${EXPS_DIR}

rm -rf ${directory}/stat.txt

for exp in ${EXPS_DIR}
do
    exp1=${exp}
    if [ ${2} == 1 ]; then
       exp1=${exp}/XGC 
       #mkdir -p ${directory1}/${exp}/subsample
       #mkdir -p ${directory1}/${exp}/particle
       mkdir -p ${directory1}/${exp}/subsample_0_2
       mkdir -p ${directory1}/${exp}/subsample_2_2
       mkdir -p ${directory1}/${exp}/particle_0_2
       mkdir -p ${directory1}/${exp}/particle_2_2
       mkdir -p ${directory1}/${exp}/simulation_0_12
       mkdir -p ${directory1}/${exp}/simulation_12_12
    else
       mkdir -p ${directory1}/${exp}/analysis
       #mkdir -p ${directory1}/${exp}/analysis1
       #mkdir -p ${directory1}/${exp}/analysis2
       mkdir -p ${directory1}/${exp}/simulation
    fi

    Nsub=`echo ${exp} | cut -d '_' -f4` 
    Npar=`echo ${exp} | cut -d '_' -f5` 
    Npar2=`echo ${exp} | cut -d '_' -f6` 
    Nstr=`echo ${exp} | cut -d '_' -f7` 

    start_time=0

    if [ -d ${directory}/${exp1}/simulation ];
    then
        start_time=`tau_convert -dumpname ${directory}/${exp1}/simulation/tautrace.0.0.0.trc ${directory}/${exp1}/simulation/events.0.edf | grep "first timestamp:" | cut -d':' -f2 | cut -d' ' -f2`
    elif [ -d ${directory}/${exp1}/simulation_0_12 ]; 
    then
        start_time=`tau_convert -dumpname ${directory}/${exp1}/simulation_0_12/tautrace.0.0.0.trc ${directory}/${exp1}/simulation_0_12/events.0.edf | grep "first timestamp:" | cut -d':' -f2 | cut -d' ' -f2`
    else
        echo "tracefiles not found!!!"
    fi

    k=0
    while [ ${k} -lt ${Nstr} ]; do
        mkdir -p ${directory1}/${exp}/stream_${k}_n0
        mkdir -p ${directory1}/${exp}/stream_${k}_n1
        let k+=1
    done

    echo "Nsub = ${Nsub}.........................."
    echo "Npar = ${Npar}.........................."
    echo "Npar2 = ${Npar2}.........................."
    echo "Nstr = ${Nstr}.........................."
    echo "Start_time = ${start_time}........................"
    
    echo "python3 read_tau_traces.py ${directory}/${exp1} ${Nsub} ${Npar} ${Npar2} ${start_time} ${directory1}/${exp} > t_${exp}.out" 
    python3 read_tau_traces.py ${directory}/${exp1} ${Nsub} ${Npar} ${Npar2} ${start_time} ${directory1}/${exp} > t_${exp}.out 
    #exit
done 
