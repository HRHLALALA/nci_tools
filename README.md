# nci_tools
Some code are directly modified from https://github.com/coecms/nci_scripts

## Usage
1. Clone this repo to your home dir.
2. In `~/.bashrc` add `export PATH="~/nci_tools:$PATH"`
3. `source ~/.bashrc`

** You can also modify `python-analysis3` to your mostly used python environment.

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
qsubi -P ${PROJECT} -t ${walltime} -n ${ngpus}
```
