#! /usr/bin/env python

import sys
import os
import re
import logging
import glob
import argparse

import sumcoevolity

import project_util

_LOG = logging.getLogger(__name__)


def get_parameter_names(number_of_comparisons):
    p = ["ln_likelihood", "concentration"]
    for i in range(number_of_comparisons):
        p.append("ln_likelihood_c{0}sp1".format(i + 1))
        p.append("root_height_c{0}sp1".format(i + 1))
        p.append("mutation_rate_c{0}sp1".format(i + 1))
        p.append("freq_1_c{0}sp1".format(i + 1))
        p.append("pop_size_c{0}sp1".format(i + 1))
        p.append("pop_size_c{0}sp2".format(i + 1))
        p.append("pop_size_root_c{0}sp1".format(i + 1))
    return p

def get_results_header(number_of_comparisons):
    h = [
            "batch",
            "sim",
            "true_model",
            "map_model",
            "true_model_cred_level",
            "map_model_p",
            "true_model_p",
            "true_num_events",
            "map_num_events",
            "true_num_events_cred_level",
        ]

    for i in range(number_of_comparisons):
        h.append("num_events_{0}_p".format(i+1))

    h.append("mean_n_var_sites")
    for i in range(number_of_comparisons):
        h.append("n_var_sites_c{0}".format(i+1))

    for p in get_parameter_names(number_of_comparisons):
        h.append("true_{0}".format(p))
        h.append("true_{0}_rank".format(p))
        h.append("mean_{0}".format(p))
        h.append("median_{0}".format(p))
        h.append("ess_{0}".format(p))
    return h

def get_empty_results_dict(number_of_comparisons):
    h = get_results_header(number_of_comparisons)
    return dict(zip(h, ([] for i in range(len(h)))))

def get_results_from_sim_rep(
        posterior_path,
        true_path,
        stdout_path,
        parameter_names,
        number_of_comparisons,
        batch_number,
        sim_number,
        burnin = 101):
    results = {}
    post_sample = sumcoevolity.posterior.PosteriorSample(
            [posterior_path],
            burnin = burnin)
    assert(post_sample.number_of_samples == 2001 - burnin)
    true_values = sumcoevolity.parsing.get_dict_from_spreadsheets(
            [true_path],
            sep = "\t",
            header = None)
    for v in true_values.values():
        assert(len(v) == 1)
    stdout = sumcoevolity.parsing.EcoevolityStdOut(stdout_path)
    assert(number_of_comparisons == stdout.number_of_comparisons)
    results["batch"] = batch_number
    results["sim"] = sim_number
    results["mean_n_var_sites"] = stdout.get_mean_number_of_variable_sites()
    for i in range(number_of_comparisons):
        results["n_var_sites_c{0}".format(i + 1)] = stdout.get_number_of_variable_sites(i)
    
    true_model = tuple(int(true_values[h][0]) for h in post_sample.height_index_keys)
    true_model_p = post_sample.get_model_probability(true_model)
    true_model_cred = post_sample.get_model_credibility_level(true_model)
    map_models = post_sample.get_map_models()
    map_model = map_models[0]
    if len(map_models) > 1:
        if true_model in map_models:
            map_model = true_model
    map_model_p = post_sample.get_model_probability(map_model)
    results["true_model"] = "".join((str(i) for i in true_model))
    results["map_model"] = "".join((str(i) for i in map_model))
    results["true_model_cred_level"] = true_model_cred
    results["map_model_p"] = map_model_p
    results["true_model_p"] = true_model_p
    
    true_nevents = int(true_values["number_of_events"][0])
    true_nevents_p = post_sample.get_number_of_events_probability(true_nevents)
    true_nevents_cred = post_sample.get_number_of_events_credibility_level(true_nevents)
    map_numbers_of_events = post_sample.get_map_numbers_of_events()
    map_nevents = map_numbers_of_events[0]
    if len(map_numbers_of_events) > 1:
        if true_nevents in map_numbers_of_events:
            map_nevents = true_nevents
    results["true_num_events"] = true_nevents
    results["map_num_events"] = map_nevents
    results["true_num_events_cred_level"] = true_nevents_cred
    for i in range(number_of_comparisons):
        results["num_events_{0}_p".format(i + 1)] = post_sample.get_number_of_events_probability(i + 1)
    
    for p in parameter_names:
        true_val = float(true_values[p][0])
        true_val_rank = post_sample.get_rank(p, true_val)
        ss = sumcoevolity.stats.SampleSummarizer(post_sample.parameter_samples[p])
        mean_val = ss.mean
        median_val = sumcoevolity.stats.median(post_sample.parameter_samples[p])
        ess = sumcoevolity.stats.effective_sample_size(
                post_sample.parameter_samples[p])
        results["true_{0}".format(p)] = true_val
        results["true_{0}_rank".format(p)] = true_val_rank
        results["mean_{0}".format(p)] = mean_val
        results["median_{0}".format(p)] = median_val
        results["ess_{0}".format(p)] = ess

    return results

def parse_simulation_results(burnin = 101):
    batch_number_pattern = re.compile(r'batch(?P<batch_number>\d+)')
    sim_number_pattern = re.compile(r'-sim-(?P<sim_number>\d+)-')
    run_number_pattern = re.compile(r'-run-(?P<sim_number>\d+)\.log')
    val_sim_dirs = glob.glob(os.path.join(project_util.VAL_DIR, '0*'))
    for val_sim_dir in val_sim_dirs:
        sim_name = os.path.basename(val_sim_dir)
        number_of_comparisons = int(sim_name[0:2])
        parameter_names = get_parameter_names(number_of_comparisons)
        header = get_results_header(number_of_comparisons)
        results_path = os.path.join(val_sim_dir, "results.csv")
        results = get_empty_results_dict(number_of_comparisons)
        var_only_results_path = os.path.join(val_sim_dir, "var-only-results.csv")
        var_only_present = False
        var_only_path = glob.glob(os.path.join(val_sim_dir, "batch*",
                "var-only-simcoevolity-sim-000*-config-state-run*log"))
        var_only_results = get_empty_results_dict(number_of_comparisons)
        if (len(var_only_path) > 0):
            var_only_present = True
        if os.path.exists(var_only_results_path):
            _LOG.warning("WARNING: Results path {0} already exists; skipping!".format(
                    var_only_results_path))
            var_only_present = False
        skipping_sim = False
        if os.path.exists(results_path):
            _LOG.warning("WARNING: Results path {0} already exists; skipping!".format(
                    results_path))
            skipping_sim = True
        if ((skipping_sim) and (not var_only_present)):
            continue

        batch_dirs = glob.glob(os.path.join(val_sim_dir, "batch*"))
        for batch_dir in sorted(batch_dirs):
            batch_number_matches = batch_number_pattern.findall(batch_dir)
            assert(len(batch_number_matches) == 1)
            batch_number_str = batch_number_matches[0]
            batch_number = int(batch_number_str)
            posterior_paths = glob.glob(os.path.join(batch_dir,
                    "simcoevolity-sim-*-config-state-run-1.log*"))
            for posterior_path in sorted(posterior_paths):
                sim_number_matches = sim_number_pattern.findall(posterior_path)
                assert(len(sim_number_matches) == 1)
                sim_number_str = sim_number_matches[0]
                sim_number = int(sim_number_str)
                sys.stdout.write("Parsing {0} batch {1} sim {2}...\n".format(
                        sim_name,
                        batch_number_str,
                        sim_number_str))
                log_paths = glob.glob(os.path.join(batch_dir,
                        "simcoevolity-sim-{0}-config-state-run-*.log*".format(
                                sim_number_str)))
                assert(len(log_paths) > 0)
                # Need to get run number of run that finished (runs are
                # sometimes pre-empted and restarted)
                run_numbers = []
                for log_path in log_paths:
                    run_number_matches = run_number_pattern.findall(log_path)
                    assert(len(run_number_matches) == 1)
                    run_numbers.append(int(run_number_matches[0]))
                run_number = sorted(run_numbers)[-1]
                post_paths = glob.glob(os.path.join(batch_dir,
                        "simcoevolity-sim-{0}-config-state-run-{1}.log*".format(
                                sim_number_str, run_number)))
                assert(len(post_paths) == 1)
                post_path = post_paths[0]
                assert(os.path.exists(post_path))
                true_paths = glob.glob(os.path.join(batch_dir,
                        "simcoevolity-sim-{0}-true-values.txt*".format(
                                sim_number_str)))
                assert(len(true_paths) == 1)
                true_path = true_paths[0]
                assert(os.path.exists(true_path))
                stdout_paths = glob.glob(os.path.join(batch_dir,
                        "simcoevolity-sim-{0}-config.yml.out*".format(
                                sim_number_str)))
                assert(len(stdout_paths) == 1)
                stdout_path = stdout_paths[0]
                assert(os.path.exists(stdout_path))
                if not skipping_sim:
                    rep_results = get_results_from_sim_rep(
                            posterior_path = post_path,
                            true_path = true_path,
                            stdout_path = stdout_path,
                            parameter_names = parameter_names,
                            number_of_comparisons = number_of_comparisons,
                            batch_number = batch_number,
                            sim_number = sim_number,
                            burnin = burnin)
                    for k, v in rep_results.items():
                        results[k].append(v)
                if var_only_present:
                    var_only_log_paths = glob.glob(os.path.join(batch_dir,
                            "var-only-simcoevolity-sim-{0}-config-state-run-*.log*".format(
                                    sim_number_str)))
                    assert(len(var_only_log_paths) > 0)
                    # Need to get run number of run that finished (runs are
                    # sometimes pre-empted and restarted)
                    var_only_run_numbers = []
                    for log_path in var_only_log_paths:
                        run_number_matches = run_number_pattern.findall(log_path)
                        assert(len(run_number_matches) == 1)
                        var_only_run_numbers.append(int(run_number_matches[0]))
                    var_only_run_number = sorted(var_only_run_numbers)[-1]
                    var_only_post_paths = glob.glob(os.path.join(batch_dir,
                            "var-only-simcoevolity-sim-{0}-config-state-run-{1}.log*".format(
                                    sim_number_str, var_only_run_number)))
                    assert(len(var_only_post_paths) == 1)
                    var_only_post_path = var_only_post_paths[0]
                    var_only_stdout_paths = glob.glob(os.path.join(batch_dir,
                            "var-only-simcoevolity-sim-{0}-config.yml.out*".format(
                                    sim_number_str)))
                    assert(len(var_only_stdout_paths) == 1)
                    var_only_stdout_path = var_only_stdout_paths[0]
                    var_only_rep_results = get_results_from_sim_rep(
                            posterior_path = var_only_post_path,
                            true_path = true_path,
                            stdout_path = var_only_stdout_path,
                            parameter_names = parameter_names,
                            number_of_comparisons = number_of_comparisons,
                            batch_number = batch_number,
                            sim_number = sim_number,
                            burnin = burnin)
                    if not skipping_sim:
                        assert(rep_results["n_var_sites_c1"] == var_only_rep_results["n_var_sites_c1"])
                    for k, v in var_only_rep_results.items():
                        var_only_results[k].append(v)
        with open(results_path, 'w') as out:
            for line in sumcoevolity.parsing.dict_line_iter(
                    results,
                    sep = '\t',
                    header = header):
                out.write(line)
        if var_only_present:
            with open(var_only_results_path, 'w') as out:
                for line in sumcoevolity.parsing.dict_line_iter(
                        var_only_results,
                        sep = '\t',
                        header = header):
                    out.write(line)

def main_cli(argv = sys.argv):
    parser = argparse.ArgumentParser()

    parser.add_argument('--burnin',
            action = 'store',
            type = int,
            default = 101,
            help = ('Number of MCMC samples to be ignored as burnin from the '
                    'beginning of every chain.'))

    if argv == sys.argv:
        args = parser.parse_args()
    else:
        args = parser.parse_args(argv)

    parse_simulation_results(burnin = args.burnin)


if __name__ == "__main__":
    main_cli()
