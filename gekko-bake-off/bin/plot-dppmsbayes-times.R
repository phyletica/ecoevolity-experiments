#! /usr/bin/env Rscript

library(ggplot2)
library(ggridges)

d = read.delim("../analyses/pymsbayes/posterior/pymsbayes-results/pymsbayes-output/d1/m1/d1-m1-s1-500000-posterior-sample.txt.gz",
        sep = "\t",
        header = T)

nsamples = length(d$PRI.t.1)
label1 = rep("Babuyan Claro | Calayan", nsamples)
label2 = rep("Maestre De Campo | Masbate", nsamples)
label3 = rep("Camiguin Norte | Dalupiri", nsamples)
comparison = c(label1, label2, label3)
time = c(d$PRI.t.1, d$PRI.t.2, d$PRI.t.3)

data <- data.frame(time = time, comparison = comparison)
data$comparison = factor(data$comparison, levels = rev(unique(as.character(data$comparison))))

ggplot(data, aes(x = time, y = comparison, height = ..density..)) +
    geom_density_ridges(stat = "density", scale = 8, rel_min_height = 0.001) +
    theme_minimal(base_size = 14) +
    theme(axis.text.y = element_text(vjust = 0)) +
    scale_x_continuous(expand = c(0.05, 0), limits = c(0, 0.008)) +
    scale_y_discrete(expand = c(0.01, 0)) +
    labs(x = "Divergence time") +
    labs(y = "")

ggsave("../results/dppmsbayes-times.pdf", width = 7.0, height = 4.32623789116916, units = "in")
ggsave("../results/dppmsbayes-times.png", width = 7.0, height = 4.32623789116916, units = "in")
r <- tryCatch(
    {
        ggsave("../results/dppmsbayes-times.svg", width = 7.0, height = 4.32623789116916, units = "in")
    },
    error = function(cond) {
        message("An error occurred while trying to save plot as SVG.")
        message("The plot has been saved in PDF and PNG format.")
        message("If you want the SVG file, you may need to install additional R packages.")
        message("Here's the original error message for details:")
        message(cond)
    },
    warning = function(cond) {
        message("A warning occurred while trying to save the plot in SVG format.")
        message("The plot has been saved in PDF and PNG format.")
        message("If you want the SVG file, you may need to install additional R packages.")
        message("Here's the original warning message for details:")
        message(cond)
    },
    finally =  {})
