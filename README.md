# Critical Mineral Procurement Model

A NetLogo model for exploring how using one, two, or three suppliers affects deliveries, unmet demand, and procurement costs in a small capacity-constrained network.

## Run the model

Open `model.nlogox` in NetLogo 7.0.4. Set the sliders, click **Setup**, then use **Step** or **Run**. Click **Setup** again after changing a slider. The model's **Info** tab explains the rules and includes a hand-check example.

## Current scope

- Three suppliers and three manufacturers with fixed relationships during each run.
- Equal order splitting across a manufacturer's selected suppliers and proportional allocation when supplier capacity is limited.
- Purchase and transport charges based on delivered units, plus a per-cycle fee for each active supplier relationship.
- Reproducible route-specific transport rates controlled by `route-seed`. Node positions are for display only.

The model reports demand, deliveries, unmet demand, fill rates, and period and cumulative costs. Inventory, disruptions, and changing supplier prices are planned for later stages.
