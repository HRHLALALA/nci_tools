# nci_tools
Some code are directly modified from https://github.com/coecms/nci_scripts

## Environment
* pandas
* python-dateutils
* pymunge

## Usage
1. Clone this repo to your home dir.
2. In `~/.bashrc` add `export PATH="~/nci_tools:$PATH"`
3. `source ~/.bashrc`

**You can also modify `python-analysis3` into your mostly used python environment.**

## Command `qcost`
```
usage: qcost.py [-h] [-q QUEUE] [-n NCPUS] [-m MEM] [-t WALLTIME] [-f FILE]

Return what it would cost (in SUs) for a PBS job submitted on gadi with the same configuration. No checking is done to ensure requests are within queue limits.

optional arguments:
  -h, --help            show this help message and exit
  -q QUEUE, --queue QUEUE
                        PBS queue
  -n NCPUS, --ncpus NCPUS
                        Number of cpus
  -m MEM, --mem MEM     Requested memory
  -t WALLTIME, --walltime WALLTIME
                        Job walltime (hours)
  -f FILE, --file FILE  target file path

```
e.g. `qcost -q normal -n 4 -m 60GB -t 3:00:00`

We also add `-f` to anlyse job file "job.sh"

e.g.: `qcost -f job.sh`

Note that we assume the `PBS_NCI_NCPUS_PER_NODE` to be 48. Therefore, the cost dominated by memory is not the same as the original one. For info: https://opus.nci.org.au/display/Help/2.2+Job+Cost+Examples

## Command `uqstat`
```
$ uqstat
                Job_Name       queue state  ncpus walltime   su     mem_pct    cpu_pct    qtime
961571.gadi-pbs    STDIN  copyq-exec     R      1 01:26:18  3.0  100.000191  85.940518 00:10:00
```

## Command `qsubi`
Alias a long command for an interactive job `qsub -I -qgpuvolta -P ${PROJECT} -lwalltime=${walltime},ncpus=$((ngpus * 12)),ngpus=${ngpus},mem=64GB,wd`
e.g.
```
qsubi -P ${PROJECT} -q ${queue} -t ${walltime} -n ${ngpus} -l ${all other arguments for -l flags}
```

## Command `create_job`

e.g. Given the same flags as `qsubi`, create a **job.sh** template in `-d`
```
create_job -d $PWD/job.sh -q ${queue} -t ${walltime} -n ${ngpus} -l ${all other arguments for -l flags}
```
In `$PWD/job.sh`
```
#!/bin/bash
#PBS -P {your project id}
#PBS -q gpuvolta
#PBS -l ncpus=12
#PBS -l mem=64GB
#PBS -l ngpus=1
#PBS -l storage=scratch/{the fold you want to mount}
#PBS -l walltime=00:40:00
#PBS -l jobfs=100GB
args=$(echo ${args}| envsubst)
args=${args//|/ }
```
**Note**: please use absolute path for `-d`, e.g. `$PWD/job.sh`

## Command `qsub_all`

e.g. Given a file say job_list.txt in current dir, `qsub_all` reads each line and run each command in this file.
```
qsub_all -f $PWD/job_list.txt
```

This command can be used with the **job.sh** file created by `create_job` command since we can pass environment $args from it

Example `job_list.txt`:
```
qsub -v args='--name=effnet|--dataset_name=imagenet|-dataset_root=$PBS_JOBFS/imagenet' job.sh
qsub -v args='--name=effnet|--dataset_name=cifar10|-dataset_root=$PBS_JOBFS/cifar10' job.sh
qsub -v args='--name=effnet|--dataset_name=cifar100|-dataset_root=$PBS_JOBFS/cifar100' job.sh
```


**Note**: please use absolute path for `-f`.


