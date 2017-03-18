#! /usr/bin/env python

import sys
import os
import logging

import sumcoevolity

import project_util

_LOG = logging.getLogger(__name__)

number_of_simulations = 1000

class PosteriorSummary(object):
    def __init__(self, paths, burnin = 0):
        self.paths = list(paths)
        self.continuous_parameter_summaries = {}
        self.number_of_event_probabilities = {}
        self.model_probabilities = {}
        self.height_index_keys = []
        self.header = []
        self.burnin = burnin
        self.number_of_samples = 0
        self._parse_posterior_paths()
    
    def _parse_posterior_paths(self):
        self.header = sumcoevolity.parsing.parse_header_from_path(self.paths[0])
        d = sumcoevolity.parsing.get_dict_from_spreadsheets(self.paths)
        self.number_of_event_probabilities = sumcoevolity.stats.get_freqs(
                (int(x) for x in d['number_of_events'][self.burnin:]))
        total_nsamples = len(d[self.header[0]])
        n = -1
        for k, v in d.items():
            if (k.startswith('generation') or 
                k.startswith('ln_likelihood') or
                k.startswith('ln_prior') or
                # k.startswith('number_of') or
                k.startswith('root_height_index')):
                continue
            self.continuous_parameter_summaries[k] = sumcoevolity.stats.get_summary(
                    (float(x) for x in v[self.burnin:]))
            if n < 0:
                n = self.continuous_parameter_summaries[k]['n']
            else:
                assert(self.continuous_parameter_summaries[k]['n'] == n)
        assert(n > -1)
        self.number_of_samples = n
        self.height_index_keys = [h for h in self.header if h.startswith('root_height_index')]
        models = []
        for i in range(self.burnin, total_nsamples):
            models.append(tuple(int(d[h][i]) for h in self.height_index_keys))
        assert len(models) == self.number_of_samples
        self.model_probabilities = sumcoevolity.stats.get_freqs(models)

    def get_models(self):
        return sorted(self.model_probabilities.items(),
                      reverse = True,
                      key = lambda x: x[1])

    def get_number_of_events(self):
        return sorted(self.number_of_event_probabilities.items(),
                      reverse = True,
                      key = lambda x: x[1])


def main_cli():
    results_dir = os.path.join(project_util.VAL_DIR, '03pairs-dpp', 'batch01')
    # results_dir = os.path.join(project_util.VAL_DIR, '03pairs-rj', 'batch01')
    # results_dir = os.path.join(project_util.VAL_DIR, '05pairs-rj', 'batch01')
    true_value_paths = []
    posterior_summaries = []
    for i in range(number_of_simulations):
        sim_index = str(i).zfill(4)
        # sim_index = str(i).zfill(3)
        true_file_path = os.path.join(
                results_dir,
                "simcoevolity-sim-" + sim_index + "-true-values.txt")
        post_path = os.path.join(
                results_dir,
                "simcoevolity-sim-" + sim_index + "-config-state-run-1.log")
        if os.path.exists(post_path):
            post_sum = PosteriorSummary([post_path], burnin = 101)
            assert(post_sum.number_of_samples == 1900)
            posterior_summaries.append(post_sum)
            true_value_paths.append(true_file_path)

    true_values = sumcoevolity.parsing.get_dict_from_spreadsheets(
            true_value_paths,
            sep = "\t",
            header = None)

    number_of_samples = len(posterior_summaries)
    for vals in true_values.values():
        # assert(len(vals) == number_of_simulations)
        assert(len(vals) == number_of_samples)
    # assert len(posterior_summaries) == number_of_simulations
    sys.stdout.write("Number of parsed posteriors: {0}\n".format(number_of_samples))

    height_index_keys = posterior_summaries[0].height_index_keys
    n_correct_model = 0
    n_model_within_95_set = 0
    n_correct_number_of_events = 0
    height_mean_path = os.path.join(results_dir, "summary-height-means.csv")
    height_median_path = os.path.join(results_dir, "summary-height-medians.csv")
    size_mean_path = os.path.join(results_dir, "summary-tip-pop-size-means.csv")
    root_size_mean_path = os.path.join(results_dir, "summary-root-pop-size-means.csv")
    size_median_path = os.path.join(results_dir, "summary-tip-pop-size-medians.csv")
    root_size_median_path = os.path.join(results_dir, "summary-root-pop-size-medians.csv")
    nevents_mean_path = os.path.join(results_dir, "summary-nevent-means.csv")
    nevents_mode_path = os.path.join(results_dir, "summary-nevent-modes.csv")
    h_mean_out = open(height_mean_path, 'w')
    h_median_out = open(height_median_path, 'w')
    nevents_out = open(nevents_mode_path, 'w')
    nevents_mean_out = open(nevents_mean_path, 'w')
    size_mean_out = open(size_mean_path, 'w')
    root_size_mean_out = open(root_size_mean_path, 'w')
    size_median_out = open(size_median_path, 'w')
    root_size_median_out = open(root_size_median_path, 'w')
    h_mean_out.write("{0},{1}\n".format("true_height", "mean_height"))
    h_median_out.write("{0},{1}\n".format("true_height", "median_height"))
    nevents_out.write("{0},{1}\n".format("true_nevents", "mode_nevents"))
    nevents_mean_out.write("{0},{1}\n".format("true_nevents", "mean_nevents"))
    size_mean_out.write("{0},{1}\n".format("true_tip_pop_size", "mean_tip_pop_size"))
    size_median_out.write("{0},{1}\n".format("true_tip_pop_size", "median_tip_pop_size"))
    root_size_mean_out.write("{0},{1}\n".format("true_root_pop_size", "mean_root_pop_size"))
    root_size_median_out.write("{0},{1}\n".format("true_root_pop_size", "median_root_pop_size"))
    for i in range(number_of_samples):
        correct_model = tuple(int(true_values[h][i]) for h in height_index_keys)
        inferred_models = posterior_summaries[i].get_models()
        inferred_model = inferred_models[0][0]
        if correct_model == inferred_model:
            n_correct_model += 1
        total_prob = 0.0
        for m, p in inferred_models:
            if m == correct_model:
                n_model_within_95_set += 1
                break
            total_prob += p
            if total_prob > 0.95:
                break
        true_nevents = int(true_values['number_of_events'][i])
        inferred_nevents = posterior_summaries[i].get_number_of_events()[0][0]
        if true_nevents == inferred_nevents:
            n_correct_number_of_events += 1

        nevents_out.write("{0},{1}\n".format(true_nevents, inferred_nevents))
        nevents_mean = posterior_summaries[i].continuous_parameter_summaries["number_of_events"]["mean"]
        nevents_mean_out.write("{0},{1}\n".format(true_nevents, nevents_mean))
        for header_key in ("root_height_c1sp1", "root_height_c2sp1", "root_height_c3sp1"):
            true_height = float(true_values[header_key][i])
            mean_height = posterior_summaries[i].continuous_parameter_summaries[header_key]['mean']
            median_height = posterior_summaries[i].continuous_parameter_summaries[header_key]['median']
            h_mean_out.write("{0},{1}\n".format(true_height, mean_height))
            h_median_out.write("{0},{1}\n".format(true_height, median_height))
        for header_key in (
                "pop_size_root_c1sp1",
                "pop_size_root_c2sp1",
                "pop_size_root_c3sp1"):
            true_size = float(true_values[header_key][i])
            mean_size = posterior_summaries[i].continuous_parameter_summaries[header_key]['mean']
            median_size = posterior_summaries[i].continuous_parameter_summaries[header_key]['median']
            root_size_mean_out.write("{0},{1}\n".format(true_size, mean_size))
            root_size_median_out.write("{0},{1}\n".format(true_size, median_size))
        for header_key in (
                "pop_size_c1sp1",
                "pop_size_c2sp1",
                "pop_size_c3sp1",
                "pop_size_c1sp2",
                "pop_size_c2sp2",
                "pop_size_c3sp2"):
            true_size = float(true_values[header_key][i])
            mean_size = posterior_summaries[i].continuous_parameter_summaries[header_key]['mean']
            median_size = posterior_summaries[i].continuous_parameter_summaries[header_key]['median']
            size_mean_out.write("{0},{1}\n".format(true_size, mean_size))
            size_median_out.write("{0},{1}\n".format(true_size, median_size))

    h_mean_out.close()
    h_median_out.close()
    nevents_out.close()
    nevents_mean_out.close()
    size_mean_out.close()
    size_median_out.close()
    root_size_mean_out.close()
    root_size_median_out.close()

    p_correct_model = n_correct_model / float(number_of_samples)
    p_correct_number_of_events = n_correct_number_of_events / float(number_of_samples)
    p_model_within_95_set = n_model_within_95_set / float(number_of_samples)
    sys.stdout.write("Number of reps with correct model in 95% credibility set: {0}\n".format(n_model_within_95_set))
    sys.stdout.write("Estimated probability of correct model in 95% credibility set: {0}\n".format(p_model_within_95_set))
    sys.stdout.write("Number of reps with correctly inferred model: {0}\n".format(n_correct_model))
    sys.stdout.write("Estimated probability of correctly inferring model: {0}\n".format(p_correct_model))
    sys.stdout.write("Number of reps with correctly inferred number of events: {0}\n".format(n_correct_number_of_events))
    sys.stdout.write("Estimated probability of correctly inferring number of events: {0}\n".format(p_correct_number_of_events))

if __name__ == "__main__":
    main_cli()
