import os
import pandas
import argparse
import re
import sys

from datetime import datetime, time, timedelta
from io import StringIO
from math import log

unit_base = {"B": 1024, "SU": 1000}


def extract_num_unit(s):
    # Match a number (possibly floating point 100.00 style) and a unit
    try:
        size, unit = re.findall(r"(\d+.\d+|\d+)\s*(\D*)$", s)[0]
    except:
        print("Failed to match size string: ", s)
        sys.exit()
    return float(size), unit


def pretty_size(n, pow=0, b=1024, u="B", pre=[""] + [p for p in "KMGTPEZY"]):
    pow, n = min(int(log(max(n * b ** pow, 1), b)), len(pre) - 1), n * b ** pow
    return "%%.%if %%s%%s" % abs(pow % (-pow - 1)) % (n / b ** float(pow), pre[pow], u)


def parse_size(size, b=1024, u="B", pre=[""] + [p for p in "KMGTPEZY"]):
    """Parse human readable file sizes, e.g. 16.4TB, 1000KSU"""
    intsize, unit = extract_num_unit(size)

    # Account for 10B vs 10KB when looking for base
    if len(unit) == len(u):
        base = unit
    else:
        base = unit[1:]

    # Check if we know this unit's base, otherwise use default
    if base in unit_base:
        b = unit_base[base]
    pow = {k + base: v for v, k in enumerate(pre)}

    return float(intsize) * (b ** pow[unit])

def parse_job_file(file_path):
    commands = {}
    with open(file_path) as f:
        for i in f.readlines():
            if not "#PBS" in i:
                continue
            _, flag, v = i.strip("\n").split(" ")
            if "-q" in flag:
                commands["queue"] = v
            elif "-l" in flag:
                if "mem" in v or "ncpus" in v or "walltime" in v:
                    k,v = v.split("=")
                    commands[k] = int(v) if "ncpus" in k else v
    return commands


def to_seconds(dt):
    """
    Convert a string like 3:00:00 to a total number of seconds.
    The formating is not strict ISO, so have to just grab the fields
    and assume %H:%M or %H:%M:%s with or without leading zeroes
    """

    f = list(map(int, dt.split(":")))
    if len(f) == 3:
        hr, m, s = f
    if len(f) == 2:
        hr, m = f
        s = 0.0
    dt = timedelta(hours=hr, minutes=m, seconds=s)

    return dt.total_seconds()


def load_data():

    queue_info_csv = StringIO(
	"""
queue,charge,ncpus,mem,jobfs
normal,2.,48,192GB,400GB
express,6.,48,192GB,400GB
hugemem,3.,48,1470GB,1400GB
megamem,5.,48,2990GB,1400GB
gpuvolta,3.,12,382GB,400GB
normalbw,1.25,28,256GB,400GB
expressbw,3.75,28,256GB,400GB
normalsl,1.5,32,192GB,400GB
hugemembw,1.25,28,1020GB,390GB
megamembw,1.25,32,3000GB,800GB
copyq,2.,1,190GB,400GB
"""
    )

    return pandas.read_csv(queue_info_csv)


def qcost(queue, ncpus, memory, walltime):
    """
    Return the cost in SUs for a PBS job
    """

    seconds_in_an_hour = 3600.0

    # Normalise time multiplier to 1 hour
    timefactor = to_seconds(walltime) / seconds_in_an_hour

    queue_info = load_data()

    info = queue_info[queue_info["queue"] == queue]

    memory = parse_size(memory)
    totalmem = parse_size(info.mem.values[0])
    cost = (
        max(ncpus, 48 * (memory / totalmem))
        * info.charge.values[0]
        * timefactor
    )
    return cost


def parse_args(args):

    parser = argparse.ArgumentParser(
        description=(
            "Return what it would cost (in SUs) for a PBS job submitted on gadi "
            +"with the same configuration. No checking is done to ensure requests "
            +"are within queue limits."
        ),
        epilog="e.g. qcost -q normal -n 4 -m 60GB -t 3:00:00 or qcost -f job.sh",
    )
    parser.add_argument("-q", "--queue", help="PBS queue", default=None)
    parser.add_argument("--abs_dir", default="./",help=argparse.SUPPRESS)
    parser.add_argument("-n", "--ncpus", help="Number of cpus", default=None, type=int)
    parser.add_argument("-m", "--mem", help="Requested memory", default=None)
    parser.add_argument("-t", "--walltime", help="Job walltime (hours)")
    parser.add_argument("-f", "--file", help="target file path")

    return parser.parse_args(args)


def main(args):
    if args.file is None:
        assert args.queue and args.ncpus and args.mem, "--queue, --ncpus, --mem are required if no -f is passed" 
    else:
        if not os.path.isabs(args.file): args.file=os.path.join(args.abs_dir, args.file)
        for k,b in parse_job_file(args.file).items():
            setattr(args, k,b)
        assert args.queue, "empty queue"
        assert args.ncpus, "empty queue"
        assert args.mem, "empty queue"
    if args.walltime is None:
        args.walltime = "1:00:00"
        print("Assuming walltime: 1:00:00")

    cost = qcost(args.queue, args.ncpus, args.mem, args.walltime)

    print(f"The cost with \033[1mqueue={args.queue}\033[0;0m, \033[1mncpus={args.ncpus}\033[0;0m and \033[1mwalltime={args.walltime}\033[0;0m is:", end = " ")
    print("\033[33m{cost}\033[0;0m".format(cost=pretty_size(cost, u="SU", b=1000.0)))
    

def main_argv():
    args = parse_args(sys.argv[1:])
    main(args)


if __name__ == "__main__":

    main_argv()
