# Critical Mineral Procurement Model

A NetLogo 7.0.4 model comparing one-, two-, and three-supplier procurement under capacity constraints and temporary supply interruptions. The default network has **5 suppliers and 10 manufacturers**; both populations are configurable.

## Run and read the interface

Open `model.nlogox` and use the controls above the network:

- **New map** initializes a new geography and updates `map-seed`.
- **Replay** initializes using the selected seeds. Use this when comparing strategies on the same external conditions.
- **Step** advances one cycle. **Run / Pause** starts or stops continuous simulation.

The two header inputs set network size: **total-suppliers = 1–20** (default 5) and **total-manufacturers = 1–50** (default 10). Both require integers. The `supplier-count` slider is the number of partners **per manufacturer**, not the total population; it cannot exceed the number of suppliers. A controlled-outage ID must also refer to an existing supplier. Invalid combinations are rejected before the current run is cleared.

The left column contains five common sliders: partner count, capacity, minimum demand, maximum demand, and failure risk. Seeds use numeric inputs. Controlled-outage timing and random-duration bounds are grouped along the bottom. After changing a setting, initialize again. Invalid bounds, fractions, or values outside the allowed ranges are rejected before clearing the current run.

The right column separates cumulative results from current-cycle charts. **Spend / unit met** divides cumulative operating expenditure by cumulative production served. Read it together with **Overall demand met**: low total spending can simply mean that little was delivered. The row beneath the network shows current production met / demand, receipts, remaining stock, and current expenditure. The cost chart replaces individual expense monitors; its labels Buy, Ship, Links, and Stock denote purchases, freight, relationship fees, and inventory holding.

At up to 16 entities, supplier labels show **orders → shipments** and manufacturer labels show **production met / demand**. Larger networks show S/M IDs; all detailed values remain available through right-click **Inspect**. Orange indicates an overloaded supplier or unmet manufacturer demand; red indicates an outage. Inspect agents or links for detailed prices, allocation shares, distances, and charges. Full rules and parameter meanings are in **Info**.

## Map size and spacing

Each entity occupies one distinct cell in a shuffled square grid, with bounded random displacement. The grid side is `max(4, ceiling(sqrt(suppliers + manufacturers)))`; cell spacing is 7.5 model units and displacement is at most ±0.6 per axis. The minimum center-to-center spacing is therefore 6.3 model units. With 20 suppliers and 50 manufacturers, the grid is 9×9 and the world is 71×71 patches, compared with 33×33 at the default population.

The network view stays 500×500 pixels through automatic patch-size adjustment. Icons get smaller as the world grows, and labels switch to IDs above 16 entities. The supported population caps keep IDs and icons readable without occupying the same cells. Procurement links can still cross. More than five simultaneous outages are summarized by count; their red nodes remain visible.

World expansion increases actual model distances and can change freight costs. Population changes can also relocate existing agents despite identical seeds. Keep populations fixed for matched sourcing-strategy comparisons. Per-supplier capacity and per-manufacturer demand are not automatically scaled: changing counts changes the aggregate supply/demand balance.

## Model rules

- Supplier base prices are drawn from 80–120; capacities are 80–120% of the capacity slider. The default 100 gives capacities 80–120, scaling the proposal's capacities to the smaller manufacturer population.
- Each manufacturer has fixed demand drawn from the selected range, initial stock of 40–80, and a stock target of one cycle's demand. Replenishment is `max(0, demand + target - opening stock)`. Stock buffers production; unmet production is lost rather than backlogged.
- Nodes occupy random positions on a schematic flat map. Freight per delivered unit is straight-line distance × 3 in interactive runs. Background regions are decorative. There are no roads, barriers, or transit delays, and distances/costs are not empirically calibrated.
- Manufacturers initially select the cheapest requested number of suppliers by base price plus freight. Contracts remain fixed. Orders shift only among established partners known to be available, with shares proportional to inverse current landed cost. Suppliers ration insufficient capacity proportionally.
- Available suppliers quote `base price × (1 + 0.20 × previous-cycle utilization)`. Utilization is actual shipments / normal capacity. Quotes never compound and cannot exceed a 20% markup. A known interrupted supplier retains its last quote; recovery uses the preceding zero-output cycle.
- New failures occur after ordering; ongoing outages are known before ordering. Controlled and independent random outages can overlap. Matched seeds preserve external supplier failures across strategies.
- Operating costs comprise purchases and freight on actual deliveries, 50 per established relationship per cycle, and 1 per unit of ending stock per cycle. Initial stock is free within the accounting horizon. There is no revenue or monetary penalty for lost production, so this model does not report profit or a single optimal strategy.

`map-seed` fixes geography. `scenario-seed` fixes base attributes, demands, initial stock, and supplier/cycle outage draws. Prices and allocation shares are endogenous and can differ across strategies under identical external conditions.

## Reproducible experiments

Two experiments are saved inside the existing model. Open **Tools → BehaviorSpace**, select an experiment, and save its table output to a location of your choice.

| Experiment | Conditions | Runs |
|---|---|---:|
| `sourcing-risk-comparison` | 1/2/3 partners × failure risk 0/2/5%; freight 3 | 270 |
| `transport-sensitivity` | 1/2/3 partners × freight 2/3/4; failure risk 2% | 270 |

Every condition uses 30 paired scenarios, each run for 500 cycles. Scenario seeds 2026–2055 pair with map seeds 1–30. Both experiments explicitly fix populations at 5 suppliers and 10 manufacturers, capacity 100, demand 30–50, random duration 1–10, and controlled outage off. Changing the interface population does not change these saved baseline experiments. The experimental initializer applies freight **before** initial supplier selection. The 90 baseline runs appear in both experiments; the two sets therefore contain 450 distinct parameter/seed combinations.

Each scenario, rather than each cycle, is an experimental replicate. Compare strategies using paired differences across the same 30 scenarios. Outputs include service level, unmet units, spending and its components, production, receipts, and starting/terminal stock. Undefined denominator metrics return `false` in BehaviorSpace and show `N/A` on the interface.

These are finite-horizon experiments, including initialization; no warm-up is discarded. They measure outcomes under the stated initial-stock policy, not an established stationary distribution.

## Executed checks and initial findings

Both saved experiments were executed with the NetLogo 7.0.4 background engine (540 completed runs of 500 cycles). With failure risk 2% and freight 3, arithmetic means across the 30 scenarios were:

| Partners per manufacturer | Demand met | Operating spend | Spend / unit met |
|---:|---:|---:|---:|
| 1 | 63.20% | 17,484,312 | 140.59 |
| 2 | 84.00% | 24,683,113 | 149.64 |
| 3 | 95.19% | 29,487,863 | 157.46 |

Units of money are abstract. More partners improve average service in these experiments while increasing operating expenditure per unit served; the table does not identify a profit-maximizing strategy. The averages are per-run summaries, not pooled ratios.

Paired strategy differences at the baseline (30 scenarios; approximate 95% Student-t intervals, 29 degrees of freedom):

| Comparison | Service gain, percentage points | Extra spend per unit met |
|---|---:|---:|
| 2 minus 1 partner | 20.80 [16.97, 24.63] | 9.04 [7.97, 10.12] |
| 3 minus 2 partners | 11.18 [7.80, 14.56] | 7.82 [7.03, 8.61] |

Intervals use the mean and sample standard deviation of **within-scenario differences**: mean ± 2.045 × SD / sqrt(30). They describe simulation uncertainty across this synthetic scenario ensemble, not uncertainty about real-world supply chains. The 90 overlapping baseline runs from the two experiment definitions agree to floating-point precision.

Even with failure risk 0%, mean service levels are 69.66%, 90.79%, and 99.67% for 1/2/3 partners. This is evidence of capacity congestion from concentrated sourcing before random failures are added. Benefits under outages must therefore be interpreted as a combination of congestion relief and disruption protection.

At risk 2%, service levels under freight coefficients 2 / 3 / 4 are respectively:

| Partners | Freight 2 | Freight 3 | Freight 4 |
|---:|---:|---:|---:|
| 1 | 57.75% | 63.20% | 68.02% |
| 2 | 75.54% | 84.00% | 87.18% |
| 3 | 92.86% | 95.19% | 96.07% |

The average service ordering persists across these tested rates, but magnitudes depend on geography and freight assumptions. This is a limited sensitivity check, not empirical validation.

Population validation additionally checked 16 network sizes across 30 map seeds each (480 layouts), including 1+1 and 20+50, grid-size boundaries, minimum spacing, image size, IDs, valid partner counts, last-supplier outage/recovery, rejection of invalid inputs, and resizing back to the baseline. The header inputs and maximum-size network were also rendered offscreen for layout review.

Verification also compared all three strategies over 500 cycles against the archived model: the interface revision preserved its numerical outcomes. Checks covered quantity/cost conservation, capacity limits, price timing, known versus surprise outages, paired external conditions, 21 invalid numeric inputs, reversed bounds, changed controls during a run, zero demand/capacity, and all suppliers interrupted.

## Interpretation and remaining work

The model supports a focused, conditional comparison of **fixed sourcing portfolios**. It already contains non-trivial interactions: shared capacity, inventory buffering, supplier interruptions, lagged price feedback, and adaptive order shares. More mechanisms are not required merely to make the model larger.

Priority follow-ups are to justify the chosen rules against literature; test capacity, relationship fees, inventory policy/initialization, and simulation horizon; and switch off price feedback in an ablation to explain its contribution. Independent outages omit common regional shocks, and fixed portfolios omit supplier replacement. Both assumptions can affect the apparent benefit of diversification. The final ODD description should document the chosen populations (5×10 for the baseline experiments), adaptive map area, and distance-based costs, rather than copy the earlier proposal's 50-manufacturer parameters.
