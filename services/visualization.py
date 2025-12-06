"""
Visualization Service
Extracted from wealth_simulator.py for better reusability and testing.
Handles all plotly chart generation for wealth simulation results.
"""
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def create_wealth_trajectory_chart(
    paths_to_plot,
    years,
    n_simulations,
    events,
    y_label,
    currency_symbol,
    starting_age,
    retirement_age,
    end_age,
    show_retirement_period=False,
    use_pension_data=False,
    total_pension_income=0
):
    """
    Create main wealth trajectory chart with Monte Carlo paths and percentiles
    
    Args:
        paths_to_plot: Wealth paths array (n_simulations x years+1)
        years: Number of simulation years
        n_simulations: Number of Monte Carlo simulations
        events: List of financial events to mark on chart
        y_label: Y-axis label (e.g., "Net Worth", "Liquid Wealth")
        currency_symbol: Currency symbol for formatting
        starting_age: User's starting age
        retirement_age: User's retirement age
        end_age: Final age in simulation
        show_retirement_period: Whether to highlight retirement period
        use_pension_data: Whether pension data is integrated
        total_pension_income: Annual pension income amount
        
    Returns:
        Plotly Figure object
    """
    # Calculate percentiles
    percentiles = [10, 25, 50, 75, 90]
    percentile_data = np.percentile(paths_to_plot, percentiles, axis=0)
    
    # Create figure
    fig = go.Figure()
    
    # Add sample paths (max 100 for performance)
    n_sample_paths = min(100, n_simulations)
    sample_indices = np.random.choice(n_simulations, n_sample_paths, replace=False)
    
    for idx in sample_indices:
        fig.add_trace(go.Scatter(
            x=list(range(years + 1)),
            y=paths_to_plot[idx],
            mode='lines',
            line=dict(color='lightblue', width=0.5),
            opacity=0.3,
            showlegend=False,
            hoverinfo='skip'
        ))
    
    # Add percentile bands
    colors = ['rgba(255,0,0,0.1)', 'rgba(255,165,0,0.15)', 'rgba(0,128,0,0.2)', 
            'rgba(255,165,0,0.15)', 'rgba(255,0,0,0.1)']
    
    fig.add_trace(go.Scatter(
        x=list(range(years + 1)),
        y=percentile_data[0],
        mode='lines',
        line=dict(width=0),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    for i in range(len(percentiles)-1):
        fig.add_trace(go.Scatter(
            x=list(range(years + 1)),
            y=percentile_data[i+1],
            mode='lines',
            line=dict(width=0),
            fill='tonexty',
            fillcolor=colors[i],
            name=f'{percentiles[i]}-{percentiles[i+1]}th percentile',
            hoverinfo='skip'
        ))
    
    # Add median line
    fig.add_trace(go.Scatter(
        x=list(range(years + 1)),
        y=percentile_data[2],
        mode='lines',
        line=dict(color='darkgreen', width=3),
        name='Median (50th percentile)'
    ))
    
    # Add event markers
    event_colors = {
        'property_purchase': 'blue',
        'property_sale': 'green',
        'one_time_expense': 'red',
        'expense_change': 'orange',
        'rental_income': 'teal',
        'windfall': 'purple'
    }
    
    for event in events:
        color = event_colors.get(event.get('type', 'unknown'), 'gray')
        fig.add_vline(
            x=event['year'],
            line_dash="dash",
            line_color=color,
            annotation_text=event['name'],
            annotation_position="top"
        )
    
    # Add retirement marker if enabled
    retirement_year = retirement_age - starting_age
    if show_retirement_period and use_pension_data and total_pension_income > 0:
        fig.add_vrect(
            x0=retirement_year,
            x1=years,
            fillcolor="rgba(255, 215, 0, 0.1)",
            layer="below",
            line_width=0,
            annotation_text="Retirement Period",
            annotation_position="top left"
        )
        fig.add_vline(
            x=retirement_year,
            line_dash="solid",
            line_color="gold",
            line_width=3,
            annotation_text=f"Retirement (Age {retirement_age})",
            annotation_position="top"
        )
    
    # Calculate y-axis range (cap at 90th percentile + 5%)
    percentile_90 = np.percentile(paths_to_plot, 90, axis=0).max()
    
    # Determine x-axis range based on retirement period toggle
    if show_retirement_period:
        # Show from retirement onwards
        x_range = [retirement_year, years]
        chart_title = f"{y_label} in Retirement: Age {retirement_age} to {end_age}"
    else:
        # Show working period + 10 years with retirement marker
        working_years_plus_10 = min(retirement_year + 10, years)
        x_range = [0, working_years_plus_10]
        chart_title = f"{y_label} Trajectory: Age {starting_age} to {starting_age + working_years_plus_10}"
        
        # Add retirement bisection line for non-retirement view
        fig.add_vline(
            x=retirement_year,
            line_dash="solid",
            line_color="gold",
            line_width=2,
            annotation_text=f"Retirement (Age {retirement_age})",
            annotation_position="top"
        )
    
    # Create tick labels with both years and age
    years_list = list(range(int(x_range[0]), int(x_range[1]) + 1))
    tick_step = max(1, len(years_list) // 10)  # Show ~10 ticks max
    tickvals = [y for i, y in enumerate(years_list) if i % tick_step == 0]
    ticktext = [f"Yr {y}<br>Age {starting_age + y}" for y in tickvals]
    
    # Update layout
    fig.update_layout(
        title=chart_title,
        xaxis_title="Years from Now / Age",
        yaxis_title=f"{y_label} ({currency_symbol})",
        hovermode='x unified',
        height=700,
        showlegend=True
    )
    
    fig.update_xaxes(
        range=x_range,
        tickvals=tickvals,
        ticktext=ticktext
    )
    
    fig.update_yaxes(
        tickprefix=currency_symbol, 
        tickformat=",.0f",
        range=[0, percentile_90 * 1.05]
    )
    
    return fig


def create_wealth_composition_chart(
    display_results,
    results,
    years,
    starting_age,
    end_age,
    currency_symbol,
    show_real=True
):
    """
    Create wealth composition chart showing liquid, pension, and property equity over time
    
    Args:
        display_results: Results in display currency
        results: Results in base currency (for inflation rates)
        years: Number of simulation years
        starting_age: User's starting age
        end_age: Final age in simulation
        currency_symbol: Currency symbol for formatting
        show_real: Whether to show inflation-adjusted values
        
    Returns:
        Plotly Figure object
    """
    fig = go.Figure()
    
    # Calculate median values
    median_liquid = np.median(display_results['liquid_wealth'], axis=0)
    median_pension = np.median(display_results['pension_wealth'], axis=0)
    median_property = np.median(display_results['property_value'], axis=0)
    median_mortgage = np.median(display_results['mortgage_balance'], axis=0)
    median_equity = median_property - median_mortgage
    median_net_worth = median_liquid + median_pension + median_equity
    
    # Apply inflation adjustment if requested
    if show_real:
        inflation_adjustment = np.concatenate([
            [1], 
            np.cumprod(1 + np.median(results['inflation_rates'], axis=0))
        ])
        median_liquid = median_liquid / inflation_adjustment
        median_pension = median_pension / inflation_adjustment
        median_equity = median_equity / inflation_adjustment
        median_net_worth = median_net_worth / inflation_adjustment
    
    # Add traces
    fig.add_trace(go.Scatter(
        x=list(range(years + 1)),
        y=median_liquid,
        mode='lines',
        name='Liquid Wealth',
        line=dict(color='#1f77b4', width=2),
        fill='tozeroy',
        fillcolor='rgba(31, 119, 180, 0.3)'
    ))
    
    fig.add_trace(go.Scatter(
        x=list(range(years + 1)),
        y=median_pension,
        mode='lines',
        name='Pension',
        line=dict(color='#ff7f0e', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=list(range(years + 1)),
        y=median_equity,
        mode='lines',
        name='Property Equity',
        line=dict(color='#2ca02c', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=list(range(years + 1)),
        y=median_net_worth,
        mode='lines',
        name='Total Net Worth',
        line=dict(color='black', width=3, dash='dash')
    ))
    
    # Add zero line
    fig.add_hline(y=0, line_dash="dot", line_color="gray", opacity=0.5)
    
    # Update layout
    fig.update_layout(
        title=f"Wealth Composition: Age {starting_age} to {end_age}",
        xaxis_title="Years from Now",
        yaxis_title=f"Value ({currency_symbol})",
        hovermode='x unified',
        height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    fig.update_yaxes(tickprefix=currency_symbol, tickformat=",.0f")
    
    return fig


def create_distribution_chart(
    paths_to_plot,
    simulation_years,
    starting_age,
    currency_symbol,
    milestone_years=None
):
    """
    Create wealth distribution histograms at key milestones
    
    Args:
        paths_to_plot: Wealth paths array (n_simulations x years+1)
        simulation_years: Number of simulation years
        starting_age: User's starting age
        currency_symbol: Currency symbol for formatting
        milestone_years: List of years to show (default: [5, 10, 15, 20, 25, 30])
        
    Returns:
        Plotly Figure object with subplots
    """
    if milestone_years is None:
        milestone_years = [5, 10, 15, 20, 25, 30]
    
    milestone_years_dist = [y for y in milestone_years if y <= simulation_years]
    
    # Determine subplot layout
    if len(milestone_years_dist) >= 3:
        n_rows = 2
        n_cols = 3
    elif len(milestone_years_dist) >= 2:
        n_rows = 1
        n_cols = len(milestone_years_dist)
    else:
        n_rows = 1
        n_cols = 1
    
    # Create subplots
    fig = make_subplots(
        rows=n_rows, cols=n_cols,
        subplot_titles=[f"Year {y} (Age {starting_age + y})" 
                       for y in milestone_years_dist[:n_rows*n_cols]]
    )
    
    # Add histograms
    for idx, year in enumerate(milestone_years_dist[:n_rows*n_cols]):
        row = idx // n_cols + 1
        col = idx % n_cols + 1
        
        if year < paths_to_plot.shape[1]:
            fig.add_trace(
                go.Histogram(
                    x=paths_to_plot[:, year],
                    nbinsx=50,
                    name=f"Year {year}",
                    showlegend=False,
                    marker_color='rgba(31, 119, 180, 0.7)'
                ),
                row=row, col=col
            )
    
    # Update layout
    fig.update_layout(
        height=400 if n_rows == 1 else 600, 
        showlegend=False
    )
    fig.update_xaxes(tickprefix=currency_symbol, tickformat=",.0f")
    fig.update_yaxes(title_text="Frequency")
    
    return fig


def get_view_type_paths(view_type, display_results, results, n_simulations, show_real=True):
    """
    Get the appropriate wealth paths based on view type selection
    
    Args:
        view_type: One of "Total Net Worth", "Liquid Wealth", "Property Equity", "Pension Wealth"
        display_results: Results in display currency
        results: Results in base currency (for inflation rates)
        n_simulations: Number of simulations
        show_real: Whether to show inflation-adjusted values
        
    Returns:
        Tuple of (paths_to_plot, y_label)
    """
    if view_type == "Total Net Worth":
        paths_to_plot = display_results['real_net_worth'] if show_real else display_results['net_worth']
        y_label = "Net Worth"
    elif view_type == "Liquid Wealth":
        paths_to_plot = display_results['liquid_wealth']
        if show_real:
            cumulative_inflation = np.cumprod(1 + results['inflation_rates'], axis=1)
            cumulative_inflation = np.column_stack([np.ones(n_simulations), cumulative_inflation])
            paths_to_plot = paths_to_plot / cumulative_inflation
        y_label = "Liquid Wealth"
    elif view_type == "Property Equity":
        paths_to_plot = display_results['property_value'] - display_results['mortgage_balance']
        if show_real:
            cumulative_inflation = np.cumprod(1 + results['inflation_rates'], axis=1)
            cumulative_inflation = np.column_stack([np.ones(n_simulations), cumulative_inflation])
            paths_to_plot = paths_to_plot / cumulative_inflation
        y_label = "Property Equity"
    else:  # Pension Wealth
        paths_to_plot = display_results['pension_wealth']
        if show_real:
            cumulative_inflation = np.cumprod(1 + results['inflation_rates'], axis=1)
            cumulative_inflation = np.column_stack([np.ones(n_simulations), cumulative_inflation])
            paths_to_plot = paths_to_plot / cumulative_inflation
        y_label = "Pension Wealth"
    
    return paths_to_plot, y_label
