# Save and Load Simulations Feature

## Overview

The FinSim Wealth Simulator now supports saving and loading complete simulation states. This allows you to:

- Save your current simulation for future reference
- Load previously saved simulations
- Compare different scenarios side-by-side
- Build a library of different life planning scenarios

## How to Use

### Saving a Simulation

1. **Run a simulation** using the sidebar controls
2. Once complete, click the **"💾 Save / Load Simulations"** expander at the top of the page
3. In the right column (**Save Current Simulation**):
   - Enter a descriptive name for your simulation
   - Click **"Save Simulation"**
4. Your simulation is now saved and can be loaded later

### Loading a Simulation

1. Click the **"💾 Save / Load Simulations"** expander
2. In the left column (**Load Simulation**):
   - Select a saved simulation from the dropdown menu
   - Click **"Load"** to restore the simulation
3. All parameters, events, and results will be restored
4. A blue indicator will show which simulation is currently loaded

### Managing Saved Simulations

- **Delete**: Select a simulation and click "Delete" to remove it
- **Rename**: After loading a simulation, you can save it again with a new name

## What Gets Saved

When you save a simulation, the following information is stored:

### Input Parameters
- Currency selection
- Initial wealth, property value, and mortgage
- Income and expenses
- Age settings (starting age, retirement age)
- All configured financial events
- Budget Builder settings (if used)

### Results
- Complete Monte Carlo simulation results
- All wealth trajectories (liquid, property, pension)
- Statistical summaries
- Probability of success metrics

### Session State
- All configuration needed to restore the exact simulation state
- Budget integration settings
- Event configurations

## Privacy and Security

- Simulations are private to your account
- Only you can view, load, or delete your saved simulations
- Exact monetary values are encrypted and stored securely
- Aggregated/anonymized data may be used for research (see Privacy Policy)

## Use Cases

### Scenario Comparison
Save different scenarios like:
- "Conservative Approach" - Lower risk, steady growth
- "Aggressive Growth" - Higher returns, more volatility
- "Early Retirement" - Retire at 55 vs 65
- "Property Purchase" - With vs without buying a home

### Life Event Planning
Create simulations for different life events:
- "Having Children" - With increased expenses
- "Career Change" - Different salary trajectory
- "Relocation" - Moving to a new country
- "Starting a Business" - Variable income scenarios

### Long-term Tracking
- Save annual snapshots of your planning
- Track how your goals evolve over time
- Compare current situation to past projections

## Tips

1. **Use Descriptive Names**: Instead of "Simulation 1", use names like "Buy house in 2027" or "Early retirement scenario"

2. **Date Your Scenarios**: Include the date or year in the name to track when you created them

3. **Document Assumptions**: Add key assumptions to the name, like "Aggressive returns (8%)" or "Conservative (5%)"

4. **Regular Updates**: Save updated simulations periodically as your situation changes

5. **Compare Variations**: Save base scenario, then make one change and save again to see the impact

## Technical Details

- Simulations are stored in PostgreSQL (production) or SQLite (local)
- Results are stored as JSON with numpy arrays serialized to lists
- Currency conversion is preserved - simulations remember their display currency
- Budget Builder integration is fully restored when loading

## Troubleshooting

### "Simulation not found or access denied"
- This simulation may have been deleted
- You may not have permission to access this simulation

### Parameters don't restore correctly
- Try running a new simulation first
- Check that you're logged in to the same account

### Results look different after loading
- Results are deterministic based on the random seed
- Currency conversion may affect display values

## Future Enhancements

Planned features:
- [ ] Share simulations with financial advisors
- [ ] Export simulation comparisons to PDF
- [ ] Simulation templates for common scenarios
- [ ] Version history for simulations
- [ ] Notes/comments on saved simulations

---

**Need help?** Contact support or check the main documentation.
