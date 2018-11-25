#!/bin/bash

directory=$1
image_path=$2

mkdir -p ${image_path}/Particle_selection
mkdir -p ${image_path}/Particle_analysis

python tau_trace_plots2_cust.py ${directory}/subsample 10 4 ${image_path}/Particle_selection
python tau_trace_plots2_cust.py ${directory}/particle 5 4 ${image_path}/Particle_analysis
