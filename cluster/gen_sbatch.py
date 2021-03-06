#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import os.path as osp
import sys
import socket
import time
import re

gres = "gpu:1"
QOS = "normal"  # high, deadline
CPU = 4
RAM = "16GB"
ENV = "conda_env"
ROOT = osp.expanduser("~/cluster")
script_dir = osp.join(ROOT, "scripts/jobs")
logs_dir = osp.join(ROOT, "scripts/output")

save_dir = osp.join(ROOT, "saved/offline")

if socket.gethostname() == "vremote":
    partition = "p100"  # or t4
    move_results = False
elif socket.gethostname() == "v":
    partition = "gpu"
    ori_savedir = save_dir
    save_dir = "/checkpoint/${USER}/${SLURM_JOB_ID}"  # temporay folder
    move_results = True
elif socket.gethostname() == "q":
    partition = "gpu"  # or t4
    move_results = False
os.makedirs(script_dir, exist_ok=True)
os.makedirs(logs_dir, exist_ok=True)

batch_sizes = [64, 128]

learning_rates = [1e-3, 3e-4, 1e-4, 3e-5, 1e-5]

dropouts = [0, 0.2]

b1s = [0.9, 0.8]

b2s = [0.999, 0.888]

weight_decays = [0.01, 0.1, 0.2]

with open("run_all.sh", "w") as allf:
    allf.write(f"cd {logs_dir}\n")
    for bs in batch_sizes:
        for lr in learning_rates:
            for do in dropouts:
                for b1 in b1s:
                    for b2 in b2s:
                        for wd in weight_decays:
                            job = f"bs{bs}_lr{lr:.1e}_drop{do}_b1{b1}_b2{b2}_weight_decay{wd}"
                            with open(f"{script_dir}/{job}.job", "w") as f:
                                f.write(f"#!/bin/bash\n")
                                f.write(f"#SBATCH -N 1\n")
                                f.write(f"#SBATCH -n 1\n")
                                f.write(f"#SBATCH --gres={gres}\n")
                                f.write(f"#SBATCH --qos={QOS}\n")
                                f.write(f"#SBATCH -p {partition}\n")
                                f.write(f"#SBATCH --cpus-per-task={CPU}\n")
                                f.write(f"#SBATCH --mem={RAM}\n")
                                f.write(f"#SBATCH --job-name={job}\n")
                                f.write(f"#SBATCH --output=%x.out\n")
                                f.write(f"cd {ROOT}\n")
                                f.write(f"source $HOME/anaconda3/etc/profile.d/conda.sh\n")
                                f.write(f"conda activate {ENV}\n")
                                f.write(
                                    f"python model.py -bs {bs} -lr {lr} -do {do} -b1 {b1} -b2 {b2} -wd {wd} -sn {job}\n")
                            allf.write(f"sbatch {script_dir}/{job}.job\n")
