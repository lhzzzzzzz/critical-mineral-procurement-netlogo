Procurement experiments — reproducibility bundle

Model checkpoint 003aefa76f89bcc5e9639fbb5a2b027589ed4597 (NetLogo 7.0.4).
The original model is unchanged. prepare.py creates a temporary observation-only copy.
No GUI actions required. Never use a quarantined/bundled Java executable on macOS;
use a trusted installed system Java (the executed study used /usr/bin/java).

macOS reproduction from this extracted folder (adjust library path for your install):
  python3 prepare.py model.nlogox
  /usr/bin/javac -cp '/Applications/NetLogo 7.0.4/app/*' StudyRunner.java
  /usr/bin/java -Xmx1536m -Djava.awt.headless=true -cp '.:/Applications/NetLogo 7.0.4/app/*' StudyRunner instrumented.nlogox runs.tsv results.jsonl
  python3 analyze.py

The runner uses two background workers. Result file ordering can differ by worker;
match rows by id, not file order. Floating point totals may differ at roundoff scale.
prepare.py fully defines all factor combinations before any outcomes are read.
1530 core runs (90 extend to1000; others500) plus 9 demos*200 =811800 cycles.
The main CSV always uses the500snapshot, including extended cases.
Fees are accounting-only; E6 revalues270traces9ways, not2430newreplicates.
summary.json holds per-condition t intervals, paired effects, windows and fee grid.
results.jsonl includes exogenous environment, 500/1000-cycle outage path, cumulative
snapshots at100/500/1000 (demo100/200), and demo per-cycle traces.
Core traces have no full per-cycle deliveries; stock_sum is accumulated per cycle.
Trace columns: cycle, demand, production_met, receipts, ending_stock, total_cost.
Metric names and definitions are in analyze.py and model Info. Mean ratios are means
of scenario ratios, not pooled ratios. Scenarios—not ticks—are replicates (n=30).
charts.py regenerates the nine figures with Python and Matplotlib (tested 3.11.2).
These are synthetic finite-horizon comparisons, not calibrated economic forecasts.
