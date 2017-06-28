#! /usr/bin/env python

import sys
import os
import re
import glob
import argparse

import project_util


batch_number_pattern = re.compile(r'batch(?P<batch_number>\d+)')
sim_number_pattern = re.compile(r'-sim-(?P<sim_number>\d+)-')
run_number_pattern = re.compile(r'-run-(?P<sim_number>\d+)\.log')

def line_count(path):
    count = 0
    with open(path) as stream:
        for line in stream:
            count += 1
    return count

def get_run_number(log_path):
    sim_number_matches = sim_number_pattern.findall(log_path)
    assert(len(sim_number_matches) == 1)
    sim_number_str = sim_number_matches[0]
    return int(sim_number_str)

def consolidate_preempted_logs(
        target_run_number = 1,
        number_of_samples = 1501):
    number_of_lines = number_of_samples + 1
    val_sim_dirs = glob.glob(os.path.join(project_util.VAL_DIR, '0*'))
    for val_sim_dir in sorted(val_sim_dirs):
        sim_name = os.path.basename(val_sim_dir)
        batch_dirs = glob.glob(os.path.join(val_sim_dir, "batch*"))
        for batch_dir in sorted(batch_dirs):
            batch_number_matches = batch_number_pattern.findall(batch_dir)
            assert(len(batch_number_matches) == 1)
            batch_number_str = batch_number_matches[0]
            batch_number = int(batch_number_str)

            posterior_paths = glob.glob(os.path.join(batch_dir,
                    "*simcoevolity-sim-*-config-state-run-{0}.log*".format(
                            target_run_number)))
            if not posterior_paths:
                sys.stderr.write("WARNING: No log files found for\n"
                        "    Simulation: {0}\n"
                        "    Batch: {1}\n"
                        "    Target run: {2}\n    Skipping!!".format(
                            sim_name,
                            batch_number,
                            target_run_number))
                continue
            for posterior_path in sorted(posterior_paths):
                sim_number_matches = sim_number_pattern.findall(posterior_path)
                assert(len(sim_number_matches) == 1)
                sim_number_str = sim_number_matches[0]
                sim_number = int(sim_number_str)
                gp = os.path.join(batch_dir,
                        "simcoevolity-sim-{0}-config-state-run-{1}.log*".format(
                                sim_number_str,
                                target_run_number))
                target_state_log_paths = glob.glob(gp)
                assert(len(target_state_log_paths) == 1, "Multiple matches to {0!r}".format(gp))
                target_state_log_path = target_state_log_paths[0]
                gp = os.path.join(batch_dir,
                        "simcoevolity-sim-{0}-config-operator-run-{1}.log*".format(
                                sim_number_str,
                                target_run_number))
                target_op_log_paths = glob.glob(gp)
                assert(len(target_op_log_paths) == 1, "Multiple matches to {0!r}".format(gp))
                target_op_log_path = target_op_log_paths[0]
                state_log_path_pattern = os.path.join(batch_dir,
                        "simcoevolity-sim-{0}-config-state-run-*.log*".format(
                                sim_number_str))
                state_log_paths = glob.glob(state_log_path_pattern)
                op_log_path_pattern = os.path.join(batch_dir,
                        "simcoevolity-sim-{0}-config-operator-run-*.log*".format(
                                sim_number_str))
                op_log_paths = glob.glob(op_log_path_pattern)
                assert(len(state_log_paths) == len(op_log_paths),
                        "{0} matches for {1!r} and {2} for {3!r}".format(
                            len(state_log_paths),
                            state_log_path_pattern,
                            len(op_log_paths),
                            op_log_path_pattern))
                assert(target_state_log_path in state_log_paths,
                        "Target {0!r} not in matches".format(
                                target_state_log_path))
                assert(target_op_log_path in op_log_paths,
                        "Target {0!r} not in matches".format(
                                target_op_log_path))
                run_numbers = sorted(get_run_number(p) for p in state_log_paths)
                assert(run_numbers == sorted(get_run_number(p) for p in op_log_paths))
                extra_run_numbers = [rn for rn in run_numbers if rn > target_run_number]
                if len(extra_run_numbers) < 1:
                    if line_count(target_state_log_path) != number_of_lines:
                        sys.stderr.write(
                                "WARNING: Target log is incomplete, but there are no extra runs\n"
                                "    Simulation: {0}\n"
                                "    Batch: {1}\n"
                                "    Rep: {2}\n"
                                "    Target run: {3}\n    Skipping!!".format(
                                        sim_name,
                                        batch_number,
                                        sim_number,
                                        target_run_number))
                    continue
                else:
                    if line_count(target_state_log_path) >= number_of_lines:
                        sys.stderr.write(
                                "WARNING: Target log is complete, but there are extra runs\n"
                                "    Simulation: {0}\n"
                                "    Batch: {1}\n"
                                "    Rep: {2}\n"
                                "    Target run: {3}\n    Skipping!!".format(
                                        sim_name,
                                        batch_number,
                                        sim_number,
                                        target_run_number))
                        continue
                    completed_run_number = extra_run_numbers.pop(-1)
                    completed_state_log_pattern = os.path.join(batch_dir,
                            "simcoevolity-sim-{0}-config-state-run-{1}.log*".format(
                                    sim_number_str,
                                    completed_run_number))
                    completed_state_log_paths = glob.glob(completed_state_log_pattern)
                    assert(len(completed_state_log_paths) == 1,
                            "Multiple matches to complete state log {0!r}".format(
                                    completed_state_log_pattern))
                    completed_state_log_path = completed_state_log_paths[0]
                    completed_op_log_pattern = os.path.join(batch_dir,
                            "simcoevolity-sim-{0}-config-operator-run-{1}.log*".format(
                                    sim_number_str,
                                    completed_run_number))
                    completed_op_log_paths = glob.glob(completed_op_log_pattern)
                    assert(len(completed_op_log_paths) == 1,
                            "Multiple matches to complete op log {0!r}".format(
                                    completed_state_log_pattern))
                    completed_op_log_path = completed_op_log_paths[0]
                    if line_count(completed_state_log_path) != number_of_lines:
                        sys.stderr.write(
                                "WARNING: could not find completed log for\n"
                                "    Simulation: {0}\n"
                                "    Batch: {1}\n"
                                "    Rep: {2}\n"
                                "    Target run: {3}\n    Skipping!!".format(
                                        sim_name,
                                        batch_number,
                                        sim_number,
                                        target_run_number))
                        continue
                    os.rename(completed_state_log_path, target_state_log_path)
                    os.rename(completed_op_log_path, target_op_log_path)
                    for n in extra_run_numbers:
                        sp = os.path.join(batch_dir,
                                "simcoevolity-sim-{0}-config-state-run-{1}.log*".format(
                                        sim_number_str,
                                        n))
                        op = os.path.join(batch_dir,
                                "simcoevolity-sim-{0}-config-operator-run-{1}.log*".format(
                                        sim_number_str,
                                        n))
                        os.remove(sp)
                        os.remove(op)
                    

def main_cli(argv = sys.argv):
    parser = argparse.ArgumentParser()

    parser.add_argument('-r', '--run-number',
            action = 'store',
            type = int,
            default = 1,
            help = 'Target run number for consolition.')
    parser.add_argument('-n', '--number-of-samples',
            action = 'store',
            type = int,
            default = 1501,
            help = ('Number of MCMC samples that should be found in the '
                    'completed log file of each analysis.'))

    if argv == sys.argv:
        args = parser.parse_args()
    else:
        args = parser.parse_args(argv)

    consolidate_preempted_logs(
            target_run_number = args.run_number,
            number_of_samples = args.number_of_samples)


if __name__ == "__main__":
    main_cli()
