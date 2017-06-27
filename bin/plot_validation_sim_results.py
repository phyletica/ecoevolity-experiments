#! /usr/bin/env python

import sys
import os
import re
import math
import glob
import logging

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)
_LOG = logging.getLogger(os.path.basename(__file__))

import sumcoevolity
import project_util

import matplotlib as mpl

# Use TrueType (42) fonts rather than Type 3 fonts
mpl.rcParams["pdf.fonttype"] = 42
mpl.rcParams["ps.fonttype"] = 42
tex_font_settings = {
        "text.usetex": True,
        "font.family": "sans-serif",
        # "font.serif": [
        #         "Computer Modern Roman",
        #         "Times",
        #         ],
        # "font.sans-serif": [
        #         "Computer Modern Sans serif",
        #         "Helvetica",
        #         ],
        # "font.cursive": [
        #         "Zapf Chancery",
        #         ],
        # "font.monospace": [
        #         "Computer Modern Typewriter",
        #         "Courier",
        #         ],
        "text.latex.preamble" : [
                "\\usepackage[T1]{fontenc}",
                "\\usepackage[cm]{sfmath}",
                ]
}

mpl.rcParams.update(tex_font_settings)

import matplotlib.pyplot as plt
from matplotlib import gridspec


def get_sequence_iter(start = 0.0, stop = 1.0, n = 10):
    assert(stop > start)
    step = (stop - start) / float(n - 1)
    return ((start + (i * step)) for i in range(n))

def truncate_color_map(cmap, min_val = 0.0, max_val = 10, n = 100):
    new_cmap = mpl.colors.LinearSegmentedColormap.from_list(
            'trunc({n},{a:.2f},{b:.2f})'.format(
                    n = cmap.name,
                    a = min_val,
                    b = max_val),
            cmap(list(get_sequence_iter(min_val, max_val, n))))
    return new_cmap

def get_root_gamma_parameters(root_alpha_string):
    shape = float(root_alpha_string)
    scale = 1.0 / shape
    return shape, scale

def get_errors(values, lowers, uppers):
    n = len(values)
    assert(n == len(lowers))
    assert(n == len(uppers))
    return [[values[i] - lowers[i] for i in range(n)],
            [uppers[i] - values[i] for i in range(n)]]


def get_results_paths(
        validatition_sim_dir,
        include_all_sizes_fixed = True,
        include_root_size_fixed = False,
        include_variable_only = True):
    dpp_500k_results_paths = []
    dpp_500k_results_paths.extend(sorted(glob.glob(os.path.join(
            validatition_sim_dir,
            "03pairs-dpp-root-[0-9][0-9][0-9][0-9]-500k",
            "results.csv.gz"))))
    if include_root_size_fixed:
        dpp_500k_results_paths.append(os.path.join(
                validatition_sim_dir,
                "03pairs-dpp-root-fixed-500k",
                "results.csv.gz"))
    if include_all_sizes_fixed:
        dpp_500k_results_paths.append(os.path.join(
                validatition_sim_dir,
                "03pairs-dpp-root-fixed-all-500k",
                "results.csv.gz"))

    vo_dpp_500k_results_paths = []
    if include_variable_only:
        vo_dpp_500k_results_paths.extend(sorted(glob.glob(os.path.join(
                validatition_sim_dir,
                "03pairs-dpp-root-[0-9][0-9][0-9][0-9]-500k",
                "var-only-results.csv.gz"))))
        if include_root_size_fixed:
            vo_dpp_500k_results_paths.append(os.path.join(
                    validatition_sim_dir,
                    "03pairs-dpp-root-fixed-500k",
                    "var-only-results.csv.gz"))
        if include_all_sizes_fixed:
            vo_dpp_500k_results_paths.append(os.path.join(
                    validatition_sim_dir,
                    "03pairs-dpp-root-fixed-all-500k",
                    "var-only-results.csv.gz"))

    dpp_100k_results_paths = []
    dpp_100k_results_paths.extend(sorted(glob.glob(os.path.join(
            validatition_sim_dir,
            "03pairs-dpp-root-[0-9][0-9][0-9][0-9]-100k",
            "results.csv.gz"))))
    if include_root_size_fixed:
        dpp_100k_results_paths.append(os.path.join(
                validatition_sim_dir,
                "03pairs-dpp-root-fixed-100k",
                "results.csv.gz"))
    if include_all_sizes_fixed:
        dpp_100k_results_paths.append(os.path.join(
                validatition_sim_dir,
                "03pairs-dpp-root-fixed-all-100k",
                "results.csv.gz"))

    vo_dpp_100k_results_paths = []
    if include_variable_only:
        vo_dpp_100k_results_paths.extend(sorted(glob.glob(os.path.join(
                validatition_sim_dir,
                "03pairs-dpp-root-[0-9][0-9][0-9][0-9]-100k",
                "var-only-results.csv.gz"))))
        if include_root_size_fixed:
            vo_dpp_100k_results_paths.append(os.path.join(
                    validatition_sim_dir,
                    "03pairs-dpp-root-fixed-100k",
                    "var-only-results.csv.gz"))
        if include_all_sizes_fixed:
            vo_dpp_100k_results_paths.append(os.path.join(
                    validatition_sim_dir,
                    "03pairs-dpp-root-fixed-all-100k",
                    "var-only-results.csv.gz"))

    if not include_variable_only:
        results_batches = {
                "500k":                 dpp_500k_results_paths,
                "100k":                 dpp_100k_results_paths,
                }
        row_keys = [
                "500k",
                "100k",
                ]
        return row_keys, results_batches

    results_batches = {
            "500k":                 dpp_500k_results_paths,
            "500k variable only":   vo_dpp_500k_results_paths,
            "100k":                 dpp_100k_results_paths,
            "100k variable only":   vo_dpp_100k_results_paths,
            }
    row_keys = [
            "500k",
            "500k variable only",
            "100k",
            "100k variable only",
            ]
    return row_keys, results_batches

def ci_width_iter(results, parameter_str):
    n = len(results["eti_95_upper_{0}".format(parameter_str)])
    for i in range(n):
        upper = float(results["eti_95_upper_{0}".format(parameter_str)][i])
        lower = float(results["eti_95_lower_{0}".format(parameter_str)][i])
        yield upper - lower

def absolute_error_iter(results, parameter_str):
    n = len(results["true_{0}".format(parameter_str)])
    for i in range(n):
        t = float(results["true_{0}".format(parameter_str)][i])
        e = float(results["mean_{0}".format(parameter_str)][i])
        yield math.fabs(t - e)


def plot_ess_versus_error(
        parameters,
        parameter_label = "divergence time",
        plot_file_prefix = None,
        include_all_sizes_fixed = True,
        include_root_size_fixed = False):
    _LOG.info("Generating ESS vs CI scatter plots for {0}...".format(parameter_label))
    root_alpha_pattern = re.compile(r'root-(?P<alpha_setting>\S+)-\d00k$')

    assert(len(parameters) == len(set(parameters)))
    if not plot_file_prefix:
        plot_file_prefix = parameters[0] 
    plot_file_prefix_ci = plot_file_prefix + "-ess-vs-ci-width"
    plot_file_prefix_error = plot_file_prefix + "-ess-vs-error"

    row_keys, results_batches = get_results_paths(project_util.VAL_DIR,
            include_all_sizes_fixed = include_all_sizes_fixed,
            include_root_size_fixed = include_root_size_fixed,
            include_variable_only = True)

    # Very inefficient, but parsing all results to get min/max for parameter
    ess_min = float('inf')
    ess_max = float('-inf')
    ci_width_min = float('inf')
    ci_width_max = float('-inf')
    error_min = float('inf')
    error_max = float('-inf')
    for key, results_batch in results_batches.items():
        for results_path in results_batch:
            results = sumcoevolity.parsing.get_dict_from_spreadsheets(
                    [results_path],
                    sep = "\t",
                    offset = 0)
            for parameter_str in parameters:
                ci_widths = tuple(ci_width_iter(results, parameter_str))
                errors = tuple(absolute_error_iter(results, parameter_str))
                ess_min = min(ess_min,
                        min(float(x) for x in results["ess_{0}".format(parameter_str)]))
                ess_max = max(ess_max,
                        max(float(x) for x in results["ess_{0}".format(parameter_str)]))
                ci_width_min = min(ci_width_min, min(ci_widths))
                ci_width_max = max(ci_width_max, max(ci_widths))
                error_min = min(error_min, min(errors))
                error_max = max(error_max, max(errors))
    ess_axis_buffer = math.fabs(ess_max - ess_min) * 0.05
    ess_axis_min = ess_min - ess_axis_buffer
    ess_axis_max = ess_max + ess_axis_buffer
    ci_width_axis_buffer = math.fabs(ci_width_max - ci_width_min) * 0.05
    ci_width_axis_min = ci_width_min - ci_width_axis_buffer
    ci_width_axis_max = ci_width_max + ci_width_axis_buffer
    error_axis_buffer = math.fabs(error_max - error_min) * 0.05
    error_axis_min = error_min - error_axis_buffer
    error_axis_max = error_max + error_axis_buffer

    plt.close('all')
    fig = plt.figure(figsize = (9, 6.5))
    nrows = len(results_batches)
    ncols = len(results_batches.values()[0])
    gs = gridspec.GridSpec(nrows, ncols,
            wspace = 0.0,
            hspace = 0.0)

    for row_idx, row_key in enumerate(row_keys):
        results_batch = results_batches[row_key]
        last_col_idx = len(results_batch) - 1
        for col_idx, results_path in enumerate(results_batch):
            sim_dir = os.path.basename(os.path.dirname(results_path))
            results_file = os.path.basename(results_path)
            root_alpha_matches = root_alpha_pattern.findall(sim_dir)
            assert(len(root_alpha_matches) == 1)
            root_alpha_setting = root_alpha_matches[0]

            results = sumcoevolity.parsing.get_dict_from_spreadsheets(
                    [results_path],
                    sep = "\t",
                    offset = 0)
            _LOG.info("row {0}, col {1} : {2}".format(row_idx, col_idx,
                    os.path.join(sim_dir, results_file)))

            x = []
            y = []
            for parameter_str in parameters:
                x.extend(float(x) for x in results["ess_{0}".format(parameter_str)])
                y.extend(ci_width_iter(results, parameter_str))

            assert(len(x) == len(y))
            ax = plt.subplot(gs[row_idx, col_idx])
            line, = ax.plot(x, y)
            plt.setp(line,
                    marker = 'o',
                    markerfacecolor = 'none',
                    markeredgecolor = '0.35',
                    markeredgewidth = 0.7,
                    markersize = 2.5,
                    linestyle = '',
                    zorder = 100,
                    rasterized = True)
            ax.set_xlim(ess_axis_min, ess_axis_max)
            ax.set_ylim(ci_width_axis_min, ci_width_axis_max)
            if row_idx == 0:
                if root_alpha_setting == "fixed-all":
                    pop_sizes = results["mean_pop_size_c1sp1"]
                    assert(len(set(pop_sizes)) == 1)
                    col_header = "$\\textrm{{\\sffamily All sizes}} = {0}$".format(pop_sizes[0])
                elif root_alpha_setting == "fixed":
                    col_header = "$\\textrm{{\\sffamily Root size}} = 1.0$"
                else:
                    root_shape, root_scale = get_root_gamma_parameters(root_alpha_setting)
                    col_header = "$\\textrm{{\\sffamily Gamma}}({0}, {1})$".format(int(root_shape), root_scale)
                ax.text(0.5, 1.0,
                        col_header,
                        horizontalalignment = "center",
                        verticalalignment = "bottom",
                        transform = ax.transAxes)
            if col_idx == last_col_idx:
                ax.text(1.0, 0.5,
                        row_key,
                        horizontalalignment = "left",
                        verticalalignment = "center",
                        rotation = 270.0,
                        transform = ax.transAxes)
    # show only the outside ticks
    all_axes = fig.get_axes()
    for ax in all_axes:
        if not ax.is_last_row():
            ax.set_xticks([])
        if not ax.is_first_col():
            ax.set_yticks([])

    # show tick labels only for lower-left plot 
    all_axes = fig.get_axes()
    for ax in all_axes:
        if ax.is_last_row() and ax.is_first_col():
            continue
        xtick_labels = ["" for item in ax.get_xticklabels()]
        ytick_labels = ["" for item in ax.get_yticklabels()]
        ax.set_xticklabels(xtick_labels)
        ax.set_yticklabels(ytick_labels)

    # avoid doubled spines
    all_axes = fig.get_axes()
    for ax in all_axes:
        for sp in ax.spines.values():
            sp.set_visible(False)
        if ax.is_first_row():
            ax.spines['top'].set_visible(True)
            ax.spines['bottom'].set_visible(True)
        else:
            ax.spines['bottom'].set_visible(True)
        if ax.is_first_col():
            ax.spines['left'].set_visible(True)
            ax.spines['right'].set_visible(True)
        else:
            ax.spines['right'].set_visible(True)

    fig.text(0.5, 0.001,
            "ESS {0}".format(parameter_label),
            horizontalalignment = "center",
            verticalalignment = "bottom",
            size = 18.0)
    fig.text(0.005, 0.5,
            "CI width {0}".format(parameter_label),
            horizontalalignment = "left",
            verticalalignment = "center",
            rotation = "vertical",
            size = 18.0)

    gs.update(left = 0.08, right = 0.98, bottom = 0.08, top = 0.97)

    plot_dir = os.path.join(project_util.VAL_DIR, "plots")
    if not os.path.exists(plot_dir):
        os.mkdir(plot_dir)
    plot_path = os.path.join(plot_dir,
            "{0}-scatter.pdf".format(plot_file_prefix_ci))
    plt.savefig(plot_path, dpi=600)
    _LOG.info("Plots written to {0!r}\n".format(plot_path))


    _LOG.info("Generating ESS vs error scatter plots for {0}...".format(parameter_label))
    plt.close('all')
    fig = plt.figure(figsize = (9, 6.5))
    nrows = len(results_batches)
    ncols = len(results_batches.values()[0])
    gs = gridspec.GridSpec(nrows, ncols,
            wspace = 0.0,
            hspace = 0.0)

    for row_idx, row_key in enumerate(row_keys):
        results_batch = results_batches[row_key]
        last_col_idx = len(results_batch) - 1
        for col_idx, results_path in enumerate(results_batch):
            sim_dir = os.path.basename(os.path.dirname(results_path))
            results_file = os.path.basename(results_path)
            root_alpha_matches = root_alpha_pattern.findall(sim_dir)
            assert(len(root_alpha_matches) == 1)
            root_alpha_setting = root_alpha_matches[0]

            results = sumcoevolity.parsing.get_dict_from_spreadsheets(
                    [results_path],
                    sep = "\t",
                    offset = 0)
            _LOG.info("row {0}, col {1} : {2}".format(row_idx, col_idx,
                    os.path.join(sim_dir, results_file)))

            x = []
            y = []
            for parameter_str in parameters:
                x.extend(float(x) for x in results["ess_{0}".format(parameter_str)])
                y.extend(absolute_error_iter(results, parameter_str))
                

            assert(len(x) == len(y))
            ax = plt.subplot(gs[row_idx, col_idx])
            line, = ax.plot(x, y)
            plt.setp(line,
                    marker = 'o',
                    markerfacecolor = 'none',
                    markeredgecolor = '0.35',
                    markeredgewidth = 0.7,
                    markersize = 2.5,
                    linestyle = '',
                    zorder = 100,
                    rasterized = True)
            ax.set_xlim(ess_axis_min, ess_axis_max)
            ax.set_ylim(error_axis_min, error_axis_max)
            if row_idx == 0:
                if root_alpha_setting == "fixed-all":
                    pop_sizes = results["mean_pop_size_c1sp1"]
                    assert(len(set(pop_sizes)) == 1)
                    col_header = "$\\textrm{{\\sffamily All sizes}} = {0}$".format(pop_sizes[0])
                elif root_alpha_setting == "fixed":
                    col_header = "$\\textrm{{\\sffamily Root size}} = 1.0$"
                else:
                    root_shape, root_scale = get_root_gamma_parameters(root_alpha_setting)
                    col_header = "$\\textrm{{\\sffamily Gamma}}({0}, {1})$".format(int(root_shape), root_scale)
                ax.text(0.5, 1.0,
                        col_header,
                        horizontalalignment = "center",
                        verticalalignment = "bottom",
                        transform = ax.transAxes)
            if col_idx == last_col_idx:
                ax.text(1.0, 0.5,
                        row_key,
                        horizontalalignment = "left",
                        verticalalignment = "center",
                        rotation = 270.0,
                        transform = ax.transAxes)
    # show only the outside ticks
    all_axes = fig.get_axes()
    for ax in all_axes:
        if not ax.is_last_row():
            ax.set_xticks([])
        if not ax.is_first_col():
            ax.set_yticks([])

    # show tick labels only for lower-left plot 
    all_axes = fig.get_axes()
    for ax in all_axes:
        if ax.is_last_row() and ax.is_first_col():
            continue
        xtick_labels = ["" for item in ax.get_xticklabels()]
        ytick_labels = ["" for item in ax.get_yticklabels()]
        ax.set_xticklabels(xtick_labels)
        ax.set_yticklabels(ytick_labels)

    # avoid doubled spines
    all_axes = fig.get_axes()
    for ax in all_axes:
        for sp in ax.spines.values():
            sp.set_visible(False)
        if ax.is_first_row():
            ax.spines['top'].set_visible(True)
            ax.spines['bottom'].set_visible(True)
        else:
            ax.spines['bottom'].set_visible(True)
        if ax.is_first_col():
            ax.spines['left'].set_visible(True)
            ax.spines['right'].set_visible(True)
        else:
            ax.spines['right'].set_visible(True)

    fig.text(0.5, 0.001,
            "ESS {0}".format(parameter_label),
            horizontalalignment = "center",
            verticalalignment = "bottom",
            size = 18.0)
    fig.text(0.005, 0.5,
            "Absolute error {0}".format(parameter_label),
            horizontalalignment = "left",
            verticalalignment = "center",
            rotation = "vertical",
            size = 18.0)

    gs.update(left = 0.08, right = 0.98, bottom = 0.08, top = 0.97)

    plot_path = os.path.join(plot_dir,
            "{0}-scatter.pdf".format(plot_file_prefix_error))
    plt.savefig(plot_path, dpi=600)
    _LOG.info("Plots written to {0!r}\n".format(plot_path))



def generate_scatter_plots(
        parameters,
        parameter_label = "divergence time",
        parameter_symbol = "\\tau",
        plot_file_prefix = None,
        include_all_sizes_fixed = True,
        include_root_size_fixed = False):
    _LOG.info("Generating scatter plots for {0}...".format(parameter_label))
    root_alpha_pattern = re.compile(r'root-(?P<alpha_setting>\S+)-\d00k$')

    assert(len(parameters) == len(set(parameters)))
    if not plot_file_prefix:
        plot_file_prefix = parameters[0] 

    row_keys, results_batches = get_results_paths(project_util.VAL_DIR,
            include_all_sizes_fixed = include_all_sizes_fixed,
            include_root_size_fixed = include_root_size_fixed,
            include_variable_only = True)

    # Very inefficient, but parsing all results to get min/max for parameter
    parameter_min = float('inf')
    parameter_max = float('-inf')
    for key, results_batch in results_batches.items():
        for results_path in results_batch:
            results = sumcoevolity.parsing.get_dict_from_spreadsheets(
                    [results_path],
                    sep = "\t",
                    offset = 0)
            for parameter_str in parameters:
                parameter_min = min(parameter_min,
                        min(float(x) for x in results["true_{0}".format(parameter_str)]))
                parameter_max = max(parameter_max,
                        max(float(x) for x in results["true_{0}".format(parameter_str)]))
                parameter_min = min(parameter_min,
                        min(float(x) for x in results["mean_{0}".format(parameter_str)]))
                parameter_max = max(parameter_max,
                        max(float(x) for x in results["mean_{0}".format(parameter_str)]))
    axis_buffer = math.fabs(parameter_max - parameter_min) * 0.05
    axis_min = parameter_min - axis_buffer
    axis_max = parameter_max + axis_buffer

    plt.close('all')
    fig = plt.figure(figsize = (9, 6.5))
    nrows = len(results_batches)
    ncols = len(results_batches.values()[0])
    gs = gridspec.GridSpec(nrows, ncols,
            wspace = 0.0,
            hspace = 0.0)

    for row_idx, row_key in enumerate(row_keys):
        results_batch = results_batches[row_key]
        last_col_idx = len(results_batch) - 1
        for col_idx, results_path in enumerate(results_batch):
            sim_dir = os.path.basename(os.path.dirname(results_path))
            results_file = os.path.basename(results_path)
            root_alpha_matches = root_alpha_pattern.findall(sim_dir)
            assert(len(root_alpha_matches) == 1)
            root_alpha_setting = root_alpha_matches[0]

            results = sumcoevolity.parsing.get_dict_from_spreadsheets(
                    [results_path],
                    sep = "\t",
                    offset = 0)
            _LOG.info("row {0}, col {1} : {2}".format(row_idx, col_idx,
                    os.path.join(sim_dir, results_file)))

            x = []
            y = []
            y_upper = []
            y_lower = []
            for parameter_str in parameters:
                x.extend(float(x) for x in results["true_{0}".format(parameter_str)])
                y.extend(float(x) for x in results["mean_{0}".format(parameter_str)])
                y_lower.extend(float(x) for x in results["eti_95_lower_{0}".format(parameter_str)])
                y_upper.extend(float(x) for x in results["eti_95_upper_{0}".format(parameter_str)])

            assert(len(x) == len(y))
            assert(len(x) == len(y_lower))
            assert(len(x) == len(y_upper))
            proportion_within_ci = sumcoevolity.stats.get_proportion_of_values_within_intervals(
                    x,
                    y_lower,
                    y_upper)
            rmse = sumcoevolity.stats.root_mean_square_error(x, y)
            _LOG.info("p(within CI) = {0:.4f}".format(proportion_within_ci))
            _LOG.info("RMSE = {0:.2e}".format(rmse))
            ax = plt.subplot(gs[row_idx, col_idx])
            line = ax.errorbar(
                    x = x,
                    y = y,
                    yerr = get_errors(y, y_lower, y_upper),
                    ecolor = '0.65',
                    elinewidth = 0.5,
                    capsize = 0.8,
                    barsabove = False,
                    marker = 'o',
                    linestyle = '',
                    markerfacecolor = 'none',
                    markeredgecolor = '0.35',
                    markeredgewidth = 0.7,
                    markersize = 2.5,
                    zorder = 100,
                    rasterized = True)
            # line, = ax.plot(x, y)
            # plt.setp(line,
            #         marker = 'o',
            #         markerfacecolor = 'none',
            #         markeredgecolor = '0.35',
            #         markeredgewidth = 0.7,
            #         linestyle = '',
            #         zorder = 100)
            ax.set_xlim(axis_min, axis_max)
            ax.set_ylim(axis_min, axis_max)
            identity_line, = ax.plot(
                    [axis_min, axis_max],
                    [axis_min, axis_max])
            plt.setp(identity_line,
                    color = '0.7',
                    linestyle = '-',
                    linewidth = 1.0,
                    marker = '',
                    zorder = 0)
            ax.text(0.02, 0.97,
                    "\\scriptsize\\noindent$p({0:s} \\in \\textrm{{\\sffamily CI}}) = {1:.3f}$".format(
                            parameter_symbol,
                            proportion_within_ci),
                    horizontalalignment = "left",
                    verticalalignment = "top",
                    transform = ax.transAxes,
                    size = 6.0,
                    zorder = 200)
            ax.text(0.02, 0.87,
                    # "\\scriptsize\\noindent$\\textrm{{\\sffamily RMSE}} = {0:.2e}$".format(
                    "\\scriptsize\\noindent RMSE = {0:.2e}".format(
                            rmse),
                    horizontalalignment = "left",
                    verticalalignment = "top",
                    transform = ax.transAxes,
                    size = 6.0,
                    zorder = 200)
            if row_idx == 0:
                if root_alpha_setting == "fixed-all":
                    pop_sizes = results["mean_pop_size_c1sp1"]
                    assert(len(set(pop_sizes)) == 1)
                    col_header = "$\\textrm{{\\sffamily All sizes}} = {0}$".format(pop_sizes[0])
                elif root_alpha_setting == "fixed":
                    col_header = "$\\textrm{{\\sffamily Root size}} = 1.0$"
                else:
                    root_shape, root_scale = get_root_gamma_parameters(root_alpha_setting)
                    col_header = "$\\textrm{{\\sffamily Gamma}}({0}, {1})$".format(int(root_shape), root_scale)
                ax.text(0.5, 1.0,
                        col_header,
                        horizontalalignment = "center",
                        verticalalignment = "bottom",
                        transform = ax.transAxes)
            if col_idx == last_col_idx:
                ax.text(1.0, 0.5,
                        row_key,
                        horizontalalignment = "left",
                        verticalalignment = "center",
                        rotation = 270.0,
                        transform = ax.transAxes)

    # show only the outside spines
    # all_axes = fig.get_axes()
    # for ax in all_axes:
    #     for sp in ax.spines.values():
    #         sp.set_visible(False)
    #     if ax.is_first_row():
    #         ax.spines['top'].set_visible(True)
    #     if ax.is_last_row():
    #         ax.spines['bottom'].set_visible(True)
    #     if ax.is_first_col():
    #         ax.spines['left'].set_visible(True)
    #     if ax.is_last_col():
    #         ax.spines['right'].set_visible(True)

    # show only the outside ticks
    all_axes = fig.get_axes()
    for ax in all_axes:
        if not ax.is_last_row():
            ax.set_xticks([])
        if not ax.is_first_col():
            ax.set_yticks([])

    # show tick labels only for lower-left plot 
    all_axes = fig.get_axes()
    for ax in all_axes:
        if ax.is_last_row() and ax.is_first_col():
            continue
        xtick_labels = ["" for item in ax.get_xticklabels()]
        ytick_labels = ["" for item in ax.get_yticklabels()]
        ax.set_xticklabels(xtick_labels)
        ax.set_yticklabels(ytick_labels)

    # avoid doubled spines
    all_axes = fig.get_axes()
    for ax in all_axes:
        for sp in ax.spines.values():
            sp.set_visible(False)
        if ax.is_first_row():
            ax.spines['top'].set_visible(True)
            ax.spines['bottom'].set_visible(True)
        else:
            ax.spines['bottom'].set_visible(True)
        if ax.is_first_col():
            ax.spines['left'].set_visible(True)
            ax.spines['right'].set_visible(True)
        else:
            ax.spines['right'].set_visible(True)

    fig.text(0.5, 0.001,
            "True {0} (${1}$)".format(parameter_label, parameter_symbol),
            horizontalalignment = "center",
            verticalalignment = "bottom",
            size = 18.0)
    fig.text(0.005, 0.5,
            "Estimated {0} ($\\bar{{{1}}}$)".format(parameter_label, parameter_symbol),
            horizontalalignment = "left",
            verticalalignment = "center",
            rotation = "vertical",
            size = 18.0)

    gs.update(left = 0.08, right = 0.98, bottom = 0.08, top = 0.97)

    plot_dir = os.path.join(project_util.VAL_DIR, "plots")
    if not os.path.exists(plot_dir):
        os.mkdir(plot_dir)
    plot_path = os.path.join(plot_dir,
            "{0}-scatter.pdf".format(plot_file_prefix))
    plt.savefig(plot_path, dpi=600)
    _LOG.info("Plots written to {0!r}\n".format(plot_path))


def generate_histograms(
        parameters,
        parameter_label = "Number of variable sites",
        plot_file_prefix = None,
        parameter_discrete = True,
        range_key = "range",
        include_all_sizes_fixed = True,
        include_root_size_fixed = False,
        include_variable_only = True):
    _LOG.info("Generating histograms for {0}...".format(parameter_label))
    assert(len(parameters) == len(set(parameters)))
    if not plot_file_prefix:
        plot_file_prefix = parameters[0] 
    root_alpha_pattern = re.compile(r'root-(?P<alpha_setting>\S+)-\d00k$')

    row_keys, results_batches = get_results_paths(project_util.VAL_DIR,
            include_all_sizes_fixed = include_all_sizes_fixed,
            include_root_size_fixed = include_root_size_fixed,
            include_variable_only = include_variable_only)

    # Very inefficient, but parsing all results to get min/max for parameter
    parameter_min = float('inf')
    parameter_max = float('-inf')
    for key, results_batch in results_batches.items():
        for results_path in results_batch:
            results = sumcoevolity.parsing.get_dict_from_spreadsheets(
                    [results_path],
                    sep = "\t",
                    offset = 0)
            for parameter_str in parameters:
                parameter_min = min(parameter_min,
                        min(float(x) for x in results["{0}".format(parameter_str)]))
                parameter_max = max(parameter_max,
                        max(float(x) for x in results["{0}".format(parameter_str)]))

    axis_buffer = math.fabs(parameter_max - parameter_min) * 0.05
    axis_min = parameter_min - axis_buffer
    axis_max = parameter_max + axis_buffer

    plt.close('all')
    if include_variable_only:
        fig = plt.figure(figsize = (9, 6.5))
    else:
        fig = plt.figure(figsize = (9, 3.25))
    nrows = len(results_batches)
    ncols = len(results_batches.values()[0])
    gs = gridspec.GridSpec(nrows, ncols,
            wspace = 0.0,
            hspace = 0.0)

    hist_bins = None
    for row_idx, row_key in enumerate(row_keys):
        results_batch = results_batches[row_key]
        last_col_idx = len(results_batch) - 1
        for col_idx, results_path in enumerate(results_batch):
            sim_dir = os.path.basename(os.path.dirname(results_path))
            results_file = os.path.basename(results_path)
            root_alpha_matches = root_alpha_pattern.findall(sim_dir)
            assert(len(root_alpha_matches) == 1)
            root_alpha_setting = root_alpha_matches[0]

            results = sumcoevolity.parsing.get_dict_from_spreadsheets(
                    [results_path],
                    sep = "\t",
                    offset = 0)
            _LOG.info("row {0}, col {1} : {2}".format(row_idx, col_idx,
                    os.path.join(sim_dir, results_file)))

            x = []
            for parameter_str in parameters:
                if parameter_discrete:
                    x.extend(int(x) for x in results["{0}".format(parameter_str)])
                else:
                    x.extend(float(x) for x in results["{0}".format(parameter_str)])

            summary = sumcoevolity.stats.get_summary(x)
            _LOG.info("0.025, 0.975 quantiles: {0:.2f}, {1:.2f}".format(
                    summary["qi_95"][0],
                    summary["qi_95"][1]))

            x_range = (parameter_min, parameter_max)
            if parameter_discrete:
                x_range = (int(parameter_min), int(parameter_max))
            ax = plt.subplot(gs[row_idx, col_idx])
            n, bins, patches = ax.hist(x,
                    normed = True,
                    bins = hist_bins,
                    range = x_range,
                    cumulative = False,
                    histtype = 'bar',
                    align = 'mid',
                    orientation = 'vertical',
                    rwidth = None,
                    log = False,
                    color = None,
                    edgecolor = '0.5',
                    facecolor = '0.5',
                    fill = True,
                    hatch = None,
                    label = None,
                    linestyle = None,
                    linewidth = None,
                    zorder = 10,
                    )
            if hist_bins is None:
                hist_bins = bins
            ax.text(1.0, 1.0,
                    "\\scriptsize {0:,} ({1:,}--{2:,})".format(
                            int(round(summary["mean"])),
                            int(round(summary[range_key][0])),
                            int(round(summary[range_key][1]))),
                    horizontalalignment = "right",
                    verticalalignment = "top",
                    transform = ax.transAxes,
                    zorder = 200)

            if row_idx == 0:
                if root_alpha_setting == "fixed-all":
                    pop_sizes = results["mean_pop_size_c1sp1"]
                    assert(len(set(pop_sizes)) == 1)
                    col_header = "$\\textrm{{\\sffamily All sizes}} = {0}$".format(pop_sizes[0])
                elif root_alpha_setting == "fixed":
                    col_header = "$\\textrm{{\\sffamily Root size}} = 1.0$"
                else:
                    root_shape, root_scale = get_root_gamma_parameters(root_alpha_setting)
                    col_header = "$\\textrm{{\\sffamily Gamma}}({0}, {1})$".format(int(root_shape), root_scale)
                ax.text(0.5, 1.0,
                        col_header,
                        horizontalalignment = "center",
                        verticalalignment = "bottom",
                        transform = ax.transAxes)
            if col_idx == last_col_idx:
                ax.text(1.0, 0.5,
                        row_key,
                        horizontalalignment = "left",
                        verticalalignment = "center",
                        rotation = 270.0,
                        transform = ax.transAxes)

    # make sure y-axis is the same
    y_max = float('-inf')
    all_axes = fig.get_axes()
    for ax in all_axes:
        ymn, ymx = ax.get_ylim()
        y_max = max(y_max, ymx)
    for ax in all_axes:
        ax.set_ylim(0.0, y_max)

    # show only the outside ticks
    all_axes = fig.get_axes()
    for ax in all_axes:
        if not ax.is_last_row():
            ax.set_xticks([])
        if not ax.is_first_col():
            ax.set_yticks([])

    # show tick labels only for lower-left plot 
    all_axes = fig.get_axes()
    for ax in all_axes:
        if ax.is_last_row() and ax.is_first_col():
            continue
        xtick_labels = ["" for item in ax.get_xticklabels()]
        ytick_labels = ["" for item in ax.get_yticklabels()]
        ax.set_xticklabels(xtick_labels)
        ax.set_yticklabels(ytick_labels)

    # avoid doubled spines
    all_axes = fig.get_axes()
    for ax in all_axes:
        for sp in ax.spines.values():
            sp.set_visible(False)
        if ax.is_first_row():
            ax.spines['top'].set_visible(True)
            ax.spines['bottom'].set_visible(True)
        else:
            ax.spines['bottom'].set_visible(True)
        if ax.is_first_col():
            ax.spines['left'].set_visible(True)
            ax.spines['right'].set_visible(True)
        else:
            ax.spines['right'].set_visible(True)

    fig.text(0.5, 0.001,
            parameter_label,
            horizontalalignment = "center",
            verticalalignment = "bottom",
            size = 18.0)
    fig.text(0.005, 0.5,
            "Density",
            horizontalalignment = "left",
            verticalalignment = "center",
            rotation = "vertical",
            size = 18.0)

    gs.update(left = 0.09, right = 0.98, bottom = 0.12, top = 0.95)

    plot_dir = os.path.join(project_util.VAL_DIR, "plots")
    if not os.path.exists(plot_dir):
        os.mkdir(plot_dir)
    plot_path = os.path.join(plot_dir,
            "{0}-histograms.pdf".format(plot_file_prefix))
    plt.savefig(plot_path)
    _LOG.info("Plots written to {0!r}\n".format(plot_path))


def generate_model_plots(
        number_of_comparisons = 3,
        include_all_sizes_fixed = True,
        include_root_size_fixed = False):
    _LOG.info("Generating model plots...")
    root_alpha_pattern = re.compile(r'root-(?P<alpha_setting>\S+)-\d00k$')
    dpp_pattern = re.compile(r'-dpp-')
    rj_pattern = re.compile(r'-rj-')
    var_only_pattern = re.compile(r'var-only-')
    number_of_comparisons = 3

    cmap = truncate_color_map(plt.cm.binary, 0.0, 0.65, 100)

    row_keys, results_batches = get_results_paths(project_util.VAL_DIR,
            include_all_sizes_fixed = include_all_sizes_fixed,
            include_root_size_fixed = include_root_size_fixed,
            include_variable_only = True)

    plt.close('all')
    fig = plt.figure(figsize = (9, 6.5))
    nrows = len(results_batches)
    ncols = len(results_batches.values()[0])
    gs = gridspec.GridSpec(nrows, ncols,
            wspace = 0.0,
            hspace = 0.0)

    for row_idx, row_key in enumerate(row_keys):
        results_batch = results_batches[row_key]
        last_col_idx = len(results_batch) - 1
        for col_idx, results_path in enumerate(results_batch):
            sim_dir = os.path.basename(os.path.dirname(results_path))
            results_file = os.path.basename(results_path)
            root_alpha_matches = root_alpha_pattern.findall(sim_dir)
            assert(len(root_alpha_matches) == 1)
            root_alpha_setting = root_alpha_matches[0]

            results = sumcoevolity.parsing.get_dict_from_spreadsheets(
                    [results_path],
                    sep = "\t",
                    offset = 0)
            _LOG.info("row {0}, col {1} : {2}".format(row_idx, col_idx,
                    os.path.join(sim_dir, results_file)))

            true_map_nevents = []
            for i in range(number_of_comparisons):
                true_map_nevents.append([0 for i in range(number_of_comparisons)])
            true_nevents = tuple(int(x) for x in results["true_num_events"])
            map_nevents = tuple(int(x) for x in results["map_num_events"])
            true_nevents_cred_levels = tuple(float(x) for x in results["true_num_events_cred_level"])
            true_model_cred_levels = tuple(float(x) for x in results["true_model_cred_level"])
            assert(len(true_nevents) == len(map_nevents))
            assert(len(true_nevents) == len(true_nevents_cred_levels))
            assert(len(true_nevents) == len(true_model_cred_levels))
            nevents_within_95_cred = 0
            model_within_95_cred = 0
            ncorrect = 0
            for i in range(len(true_nevents)):
                # true_map_nevents[true_nevents[i] - 1][map_nevents[i] - 1] += 1
                true_map_nevents[map_nevents[i] - 1][true_nevents[i] - 1] += 1
                if true_nevents_cred_levels[i] <= 0.95:
                    nevents_within_95_cred += 1
                if true_model_cred_levels[i] <= 0.95:
                    model_within_95_cred += 1
                if true_nevents[i] == map_nevents[i]:
                    ncorrect += 1
            p_nevents_within_95_cred = nevents_within_95_cred / float(len(true_nevents))
            p_model_within_95_cred = model_within_95_cred / float(len(true_nevents))
            p_correct = ncorrect / float(len(true_nevents))

            _LOG.info("p(nevents within CS) = {0:.4f}".format(p_nevents_within_95_cred))
            _LOG.info("p(model within CS) = {0:.4f}".format(p_model_within_95_cred))
            ax = plt.subplot(gs[row_idx, col_idx])

            ax.imshow(true_map_nevents,
                    origin = 'lower',
                    cmap = cmap,
                    aspect = 'auto',
                    )
            for i, row_list in enumerate(true_map_nevents):
                for j, num_events in enumerate(row_list):
                    ax.text(j, i,
                            str(num_events),
                            horizontalalignment = "center",
                            verticalalignment = "center")
            ax.text(0.99, 0.01,
                    "\\scriptsize$p(n \\in 95\\% \\textrm{{\\sffamily CS}}) = {0:.3f}$".format(
                            p_nevents_within_95_cred),
                    horizontalalignment = "right",
                    verticalalignment = "bottom",
                    transform = ax.transAxes)
            ax.text(0.01, 0.99,
                    "\\scriptsize$p(\\bar{{n}} = n) = {0:.3f}$".format(
                            p_correct),
                    horizontalalignment = "left",
                    verticalalignment = "top",
                    transform = ax.transAxes)
            if row_idx == 0:
                if root_alpha_setting == "fixed-all":
                    pop_sizes = results["mean_pop_size_c1sp1"]
                    assert(len(set(pop_sizes)) == 1)
                    col_header = "$\\textrm{{\\sffamily All sizes}} = {0}$".format(pop_sizes[0])
                elif root_alpha_setting == "fixed":
                    col_header = "$\\textrm{{\\sffamily Root size}} = 1.0$"
                else:
                    root_shape, root_scale = get_root_gamma_parameters(root_alpha_setting)
                    col_header = "$\\textrm{{\\sffamily Gamma}}({0}, {1})$".format(int(root_shape), root_scale)
                ax.text(0.5, 1.0,
                        col_header,
                        horizontalalignment = "center",
                        verticalalignment = "bottom",
                        transform = ax.transAxes)
            if col_idx == last_col_idx:
                ax.text(1.0, 0.5,
                        row_key,
                        horizontalalignment = "left",
                        verticalalignment = "center",
                        rotation = 270.0,
                        transform = ax.transAxes)

    # show only the outside ticks
    all_axes = fig.get_axes()
    for ax in all_axes:
        if not ax.is_last_row():
            ax.set_xticks([])
        if not ax.is_first_col():
            ax.set_yticks([])

    # show tick labels only for lower-left plot 
    all_axes = fig.get_axes()
    for ax in all_axes:
        if ax.is_last_row() and ax.is_first_col():
            xtick_labels = [item for item in ax.get_xticklabels()]
            for i in range(1, len(xtick_labels) - 1):
                xtick_labels[i].set_text(str(i))
            ytick_labels = [item for item in ax.get_yticklabels()]
            for i in range(1, len(ytick_labels) - 1):
                ytick_labels[i].set_text(str(i))
            ax.set_xticklabels(xtick_labels)
            ax.set_yticklabels(ytick_labels)
        else:
            xtick_labels = ["" for item in ax.get_xticklabels()]
            ytick_labels = ["" for item in ax.get_yticklabels()]
            ax.set_xticklabels(xtick_labels)
            ax.set_yticklabels(ytick_labels)

    # avoid doubled spines
    all_axes = fig.get_axes()
    for ax in all_axes:
        for sp in ax.spines.values():
            sp.set_visible(False)
        if ax.is_first_row():
            ax.spines['top'].set_visible(True)
            ax.spines['bottom'].set_visible(True)
        else:
            ax.spines['bottom'].set_visible(True)
        if ax.is_first_col():
            ax.spines['left'].set_visible(True)
            ax.spines['right'].set_visible(True)
        else:
            ax.spines['right'].set_visible(True)

    fig.text(0.5, 0.001,
            "True number of events",
            horizontalalignment = "center",
            verticalalignment = "bottom",
            size = 18.0)
    fig.text(0.005, 0.5,
            "Estimated number of events",
            horizontalalignment = "left",
            verticalalignment = "center",
            rotation = "vertical",
            size = 18.0)

    gs.update(left = 0.08, right = 0.98, bottom = 0.08, top = 0.97)

    plot_dir = os.path.join(project_util.VAL_DIR, "plots")
    if not os.path.exists(plot_dir):
        os.mkdir(plot_dir)
    plot_path = os.path.join(plot_dir,
            "nevents.pdf")
    plt.savefig(plot_path)
    _LOG.info("Plots written to {0!r}\n".format(plot_path))


def main_cli(argv = sys.argv):
    generate_scatter_plots(
            parameters = [
                    "root_height_c1sp1",
                    "root_height_c2sp1",
                    "root_height_c3sp1",
                    ],
            parameter_label = "divergence time",
            parameter_symbol = "\\tau",
            plot_file_prefix = "div-time",
            include_all_sizes_fixed = True,
            include_root_size_fixed = False)
    generate_scatter_plots(
            parameters = [
                    "pop_size_root_c1sp1",
                    "pop_size_root_c2sp1",
                    "pop_size_root_c3sp1",
                    ],
            parameter_label = "root population size",
            parameter_symbol = "N_e\\mu",
            plot_file_prefix = "root-pop-size",
            include_all_sizes_fixed = False,
            include_root_size_fixed = False)
    generate_scatter_plots(
            parameters = [
                    "pop_size_c1sp1",
                    "pop_size_c2sp1",
                    "pop_size_c3sp1",
                    ],
            parameter_label = "leaf population size",
            parameter_symbol = "N_e\\mu",
            plot_file_prefix = "leaf-pop-size",
            include_all_sizes_fixed = False,
            include_root_size_fixed = False)
    generate_model_plots(
            number_of_comparisons = 3,
            include_all_sizes_fixed = True,
            include_root_size_fixed = False)
    generate_histograms(
            parameters = [
                    "n_var_sites_c1",
                    "n_var_sites_c2",
                    "n_var_sites_c3",
                    ],
            parameter_label = "Number of variable sites",
            plot_file_prefix = "number-of-variable-sites",
            parameter_discrete = True,
            range_key = "range",
            include_all_sizes_fixed = True,
            include_root_size_fixed = False,
            include_variable_only = False)
    generate_histograms(
            parameters = [
                    "ess_ln_likelihood",
                    ],
            parameter_label = "Effective samples size of log likelihood",
            plot_file_prefix = "ess-ln-likelihood",
            parameter_discrete = False,
            range_key = "range",
            include_all_sizes_fixed = True,
            include_root_size_fixed = False,
            include_variable_only = True)
    generate_histograms(
            parameters = [
                    "ess_root_height_c1sp1",
                    "ess_root_height_c2sp1",
                    "ess_root_height_c3sp1",
                    ],
            parameter_label = "Effective samples size of divergence time",
            plot_file_prefix = "ess-div-time",
            parameter_discrete = False,
            range_key = "range",
            include_all_sizes_fixed = True,
            include_root_size_fixed = False,
            include_variable_only = True)
    generate_histograms(
            parameters = [
                    "ess_pop_size_root_c1sp1",
                    "ess_pop_size_root_c2sp1",
                    "ess_pop_size_root_c3sp1",
                    ],
            parameter_label = "Effective samples size of root population size",
            plot_file_prefix = "ess-root-pop-size",
            parameter_discrete = False,
            range_key = "range",
            include_all_sizes_fixed = False,
            include_root_size_fixed = False,
            include_variable_only = True)
    plot_ess_versus_error(
            parameters = [
                    "root_height_c1sp1",
                    "root_height_c2sp1",
                    "root_height_c3sp1",
                    ],
            parameter_label = "divergence time",
            plot_file_prefix = "div-time",
            include_all_sizes_fixed = True,
            include_root_size_fixed = False)


if __name__ == "__main__":
    main_cli()
