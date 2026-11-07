# Generate integers 0..n-1 with R's sample(), old ("Rounding") and new ("Rejection") methods.
# Usage: Rscript src/languages/r/sample_r.R <n> <N> <seed> <outdir>
args <- commandArgs(trailingOnly = TRUE)
n <- as.numeric(args[1]); N <- as.integer(args[2]); seed <- as.integer(args[3]); outdir <- args[4]
dir.create(outdir, recursive = TRUE, showWarnings = FALSE)
for (k in c("Rounding", "Rejection")) {
  suppressWarnings(RNGkind("Mersenne-Twister", "Inversion", k))
  set.seed(seed)
  y <- sample.int(n, N, replace = TRUE) - 1
  f <- file.path(outdir, sprintf("r_%s_n%s_N%d_seed%d.txt", k, format(n, scientific = FALSE), N, seed))
  write(format(y, scientific = FALSE, trim = TRUE), f, ncolumns = 1)
  cat(f, "\n")
}
