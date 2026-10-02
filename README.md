# Critical Mineral Procurement Model

A NetLogo model comparing one-, two-, and three-supplier procurement strategies under capacity limits and temporary supply interruptions.

## Run

Open `model.nlogox` in NetLogo 7.0.4. **Setup** builds a new random map; **Replay** rebuilds the map shown by `map-seed`. Use **Step** for one cycle or **Run** for continuous simulation. After editing controls, initialize again. For a fair strategy comparison, change `supplier-count` and click **Replay** to keep the same map and external conditions.

The **Info** tab documents parameters, formulas, controls, and examples.

## Stage 9

- **5 suppliers and 10 manufacturers**, randomly placed on a schematic flat map. Positions stay fixed during each run; background regions are decorative.
- Supplier base prices vary from 80–120. Available suppliers quote `base price × (1 + 0.20 × previous-cycle utilization)`, using actual shipments divided by normal capacity. Markups are bounded at 20% and never compound. Capacity varies from 80–120% of the capacity slider; its default of 100 gives 80–120 units per supplier. This scales the proposal's capacities down for the smaller manufacturer population.
- Transportation cost per delivered unit equals straight-line map distance × a fixed coefficient of 3. A purchase-price discount of 15 compensates for 5 extra map units of travel; both the selection rule and paid transport charges use this rate. This replaces the earlier randomly assigned route rates. Distances and costs are illustrative, not calibrated physical units.
- Each manufacturer chooses the requested number of suppliers with the lowest purchase price plus transport cost per unit. Contracts remain fixed; each cycle orders are split among known-available partners in proportion to the inverse of their current landed unit costs. If none are available, replenishment is recorded as unplaced. Suppliers ration limited capacity proportionally.
- Initial inventory is 40–80 units per manufacturer, with a target of one cycle's demand. Orders cover production and replenish stock. Unmet demand is measured after inventory is used.
- Costs include purchases and transport on actual deliveries, 50 per established supplier relationship per cycle, and 1 per unit of ending inventory per cycle.
- One controlled outage can target S1–S5. Independent random outages use the configured risk and duration range. New outages interrupt after orders; ongoing outages are known before next-cycle ordering, so orders can shift to remaining established partners.
- `scenario-seed` reproduces supplier base attributes, demands, initial stocks, and outage draws. Prices and order shares subsequently respond to each strategy's own outcomes. `map-seed` reproduces geography. Matched Replay runs keep external conditions identical across sourcing strategies.

The interface reports deliveries, production demand met, unmet demand, remaining inventory, and separate period/cumulative costs. Supplier labels show orders → shipments; manufacturer labels show demand met / demand.

The interface also shows average supplier price and actual utilization. Inspect a link to see its current landed cost and order share. A manufacturer with only one partner cannot redirect an order to an unconnected supplier. Stage 10 will run matched multi-seed experiments; partner replacement, travel time, roads, and elevation remain outside this model.

## Price–distance balance

The freight coefficient was increased from 1 to 3 while keeping base purchase prices at 80–120. Across 100 maps × 30 price scenarios, initial single-supplier selection placed all ten manufacturers with one supplier in 9 of 3,000 combinations, compared with 470 under the old rate. The coefficient is illustrative, not empirically calibrated; concentration remains possible.

For the example `map-seed = 2267`, `scenario-seed = 2026`, and `supplier-count = 1`, click **Replay**: S1–S5 attract 2, 2, 5, 0, and 1 manufacturers respectively. All ten previously selected S3.
