#! /usr/bin/env python

import sys
import os
import logging

import sumcoevolity

import project_util

_LOG = logging.getLogger(__name__)

number_of_simulations = 100

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
                k.startswith('number_of') or
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
    # results_dir = os.path.join(project_util.VAL_DIR, '03pairs-dpp', 'batch01')
    results_dir = os.path.join(project_util.VAL_DIR, '03pairs-rj', 'batch01')
    true_value_paths = []
    posterior_summaries = []
    for i in range(number_of_simulations):
        sim_index = str(i).zfill(4)
        true_file_path = os.path.join(
                results_dir,
                "simcoevolity-sim-" + sim_index + "-true-values.txt")
        true_value_paths.append(true_file_path)
        post_path = os.path.join(
                results_dir,
                "simcoevolity-sim-" + sim_index + "-config-state-run-1.log")
        if os.path.exists(post_path):
            post_sum = PosteriorSummary([post_path], burnin = 101)
            # assert(post_sum.number_of_samples == 1900)
            posterior_summaries.append(post_sum)

    true_values = sumcoevolity.parsing.get_dict_from_spreadsheets(
            true_value_paths,
            sep = "\t",
            header = None)

    for vals in true_values.values():
        assert(len(vals) == number_of_simulations)
    assert len(posterior_summaries) == number_of_simulations

    height_index_keys = posterior_summaries[0].height_index_keys
    n_correct_model = 0
    n_correct_number_of_events = 0
    for i in range(number_of_simulations):
        correct_model = tuple(int(true_values[h][i]) for h in height_index_keys)
        inferred_model = posterior_summaries[i].get_models()[0][0]
        print correct_model
        print posterior_summaries[i].get_models()
        print "\n"
        if correct_model == inferred_model:
            n_correct_model += 1
        if int(true_values['number_of_events'][i]) == posterior_summaries[i].get_number_of_events()[0][0]:
            n_correct_number_of_events += 1

    p_correct_model = n_correct_model / float(number_of_simulations)
    p_correct_number_of_events = n_correct_number_of_events / float(number_of_simulations)
    sys.stdout.write("Number of reps with correctly inferred model: {0}\n".format(n_correct_model))
    sys.stdout.write("Estimated probability of correctly inferring model: {0}\n".format(p_correct_model))
    sys.stdout.write("Number of reps with correctly inferred number of events: {0}\n".format(n_correct_number_of_events))
    sys.stdout.write("Estimated probability of correctly inferring number of events: {0}\n".format(p_correct_number_of_events))

if __name__ == "__main__":
    main_cli()