#!/bin/bash

declare -a directory=("Latest_Results_70" "Latest_Results_80" "Latest_Results_90")
declare -a xlsx_file=("Particle_Selection.xlsx" "Particle_Analysis.xlsx")
declare -a column1=("B" "M" "X" "AJ")
declare -a column2=("B" "M" "X" "AJ")
declare -a EXPS_DIR=("Images-EclusiveN" "Images-sharedN-ExcP" "Images-sharedN-SharedP" "Images-sharedN-DefP")

i=0

for path in ${directory[@]}
do
   j=0
   for exps in ${EXPS_DIR[@]}
   do
      python3 into_excel.py ${path}/xlsx_file[0] column1[${j}] ${path}/${exps}/Particle_selection  
      python3 into_excel.py ${path}/xlsx_file[1] column2[${j}] ${path}/${exps}/Particle_analysis  
      j=`expr $j + 1`
   done
   i=`expr $i + 1`
done 
