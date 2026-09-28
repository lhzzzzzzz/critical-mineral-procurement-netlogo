# Critical Mineral Procurement Model

A NetLogo model for exploring how using one, two, or three suppliers affects deliveries, unmet demand, and procurement costs in a small capacity-constrained network.

## Run the model

Open `model.nlogox` in NetLogo 7.0.4. Set the sliders, click **Setup**, then use **Step** or **Run**. Click **Setup** again after changing a slider. The model's **Info** tab explains the rules and includes a hand-check example.

## Current scope

- Three suppliers and three manufacturers with fixed relationships during each run.
- Equal order splitting across a manufacturer's selected suppliers and proportional allocation when supplier capacity is limited.
- Purchase and transport charges based on delivered units, plus a per-cycle fee for each active supplier relationship.
- Reproducible route-specific transport rates controlled by `route-seed`. Node positions are for display only.
- One scheduled, complete supplier outage with a chosen start cycle and duration. Orders and relationships remain fixed during the outage, and normal supply resumes afterward.
- Independent random supplier outages with a configurable per-cycle risk and duration range. `scenario-seed` reproduces manufacturer demands and outage events across sourcing strategies.

The model reports demand, deliveries, unmet demand, fill rates, and period and cumulative costs. Inventory, supplier switching, and changing supplier prices are planned for later stages.
