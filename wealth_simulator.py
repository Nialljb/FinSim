import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import io
from reportlab.lib.colors import HexColor, whitesmoke, beige, black
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import plotly.io as pio
from auth import initialize_session_state, show_login_page, show_user_header, check_simulation_limit, increment_simulation_count, increment_export_count, reset_simulation_count
from data_tracking import save_simulation, save_full_simulation, load_simulation, get_user_simulations, delete_simulation, update_simulation_name
from database import init_db
from alt_landing_page import show_landing_page
from currency_converter import get_exchange_rates, convert_currency, show_currency_info

# ADD THESE LINES after the existing currency_converter import:

from currency_manager import (
    BASE_CURRENCY,
    initialize_currency_system,
    to_base_currency,
    from_base_currency,
    format_currency,
    get_display_value,
    handle_currency_change,
    convert_events_to_base,
    convert_events_from_base,
    convert_simulation_results_to_display,  # ← Make sure this is here
    create_currency_info_widget,
)

# FIND THIS LINE (around line 35):
initialize_session_state()

# ADD THIS LINE IMMEDIATELY AFTER IT:
initialize_currency_system()

# Set page config - ONCE at the top
st.set_page_config(
    page_title="FinSim - Financial Planning",
    page_icon="💰",
    layout="wide",
)

# Initialize database on first run
try:
    init_db()
except:
    pass

# Initialize session state
initialize_session_state()

# Initialize currency system
initialize_currency_system()

# Authentication check
if not st.session_state.get('authenticated', False):
    show_landing_page()
    st.stop()

# Show user header
show_user_header()

# Global CSS for tab fonts
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.5rem !important;
        font-weight: 600 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Check PDF export availability
try:
    import plotly.io as pio
    test_fig = go.Figure()
    pio.to_image(test_fig, format='png', width=10, height=10)
    PDF_EXPORT_AVAILABLE = True
except Exception as e:
    PDF_EXPORT_AVAILABLE = False
    print(f"PDF export unavailable: {e}")

# Currency configuration
CURRENCIES = {
    'EUR': {'symbol': '€', 'name': 'Euro', 'locale': 'de_DE'},
    'GBP': {'symbol': '£', 'name': 'British Pound', 'locale': 'en_GB'},
    'CAD': {'symbol': 'C$', 'name': 'Canadian Dollar', 'locale': 'en_CA'},
    'USD': {'symbol': '$', 'name': 'US Dollar', 'locale': 'en_US'},
    'AUD': {'symbol': 'A$', 'name': 'Australian Dollar', 'locale': 'en_AU'},
    'NZD': {'symbol': 'NZ$', 'name': 'New Zealand Dollar', 'locale': 'en_NZ'},
    'CHF': {'symbol': 'CHF', 'name': 'Swiss Franc', 'locale': 'de_CH'},
    'SEK': {'symbol': 'kr', 'name': 'Swedish Krona', 'locale': 'sv_SE'},
    'NOK': {'symbol': 'kr', 'name': 'Norwegian Krone', 'locale': 'nb_NO'},
    'DKK': {'symbol': 'kr', 'name': 'Danish Krone', 'locale': 'da_DK'},
    'JPY': {'symbol': '¥', 'name': 'Japanese Yen', 'locale': 'ja_JP'},
    'CNY': {'symbol': '¥', 'name': 'Chinese Yuan', 'locale': 'zh_CN'},
    'INR': {'symbol': '₹', 'name': 'Indian Rupee', 'locale': 'hi_IN'},
    'SGD': {'symbol': 'S$', 'name': 'Singapore Dollar', 'locale': 'en_SG'},
    'HKD': {'symbol': 'HK$', 'name': 'Hong Kong Dollar', 'locale': 'zh_HK'},
}

# Helper function for Excel export
def export_to_excel(results, currency_symbol, selected_currency, events, 
                    gross_annual_income, monthly_expenses, initial_liquid_wealth,
                    initial_property_value, initial_mortgage):
    """Export simulation results to Excel file"""
    output = io.BytesIO()
    
    # ADD THESE LINES AT THE TOP:
    # Convert results and events for export
    export_results = convert_simulation_results_to_display(results, selected_currency)
    export_events = convert_events_from_base(events, selected_currency)
    
    # Convert input values for export
    export_income = from_base_currency(gross_annual_income, selected_currency)
    export_expenses = from_base_currency(monthly_expenses, selected_currency)
    export_liquid = from_base_currency(initial_liquid_wealth, selected_currency)
    export_property = from_base_currency(initial_property_value, selected_currency)
    export_mortgage = from_base_currency(initial_mortgage, selected_currency)
    
    # NOW USE export_results, export_events, and export_* values in the rest of the function
    # Change all instances of 'results' to 'export_results'
    # Change all instances of 'events' to 'export_events'
    # Change all instances of input values to their export_* versions
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book
        
        currency_format = workbook.add_format({'num_format': f'{currency_symbol}#,##0'})
        percent_format = workbook.add_format({'num_format': '0.0%'})
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4CAF50',
            'font_color': 'white',
            'border': 1
        })
        
        actual_years = export_results['net_worth'].shape[1] - 1
        years_array = np.arange(0, actual_years + 1)
        
        # Add currency info sheet
        currency_info = pd.DataFrame({
            'Setting': ['Export Currency', 'Base Currency', 'Export Date'],
            'Value': [selected_currency, BASE_CURRENCY, datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        })
        currency_info.to_excel(writer, sheet_name='Currency Info', index=False)
        
        # Summary Statistics
        summary_data = {
            'Metric': [
                'Median Final Net Worth',
                'Mean Final Net Worth',
                '10th Percentile Final Net Worth',
                '90th Percentile Final Net Worth',
                'Probability of Growth',
                'Probability of 2x Growth',
                '',
                'Initial Inputs',
                'Gross Annual Income',
                'Monthly Expenses',
                'Initial Liquid Wealth',
                'Initial Property Value',
                'Initial Mortgage'
            ],
            'Value': [
                np.median(export_results['net_worth'][:, -1]),
                np.mean(export_results['net_worth'][:, -1]),
                np.percentile(export_results['net_worth'][:, -1], 10),
                np.percentile(export_results['net_worth'][:, -1], 90),
                (export_results['net_worth'][:, -1] > export_results['net_worth'][:, 0]).mean(),
                (export_results['net_worth'][:, -1] > export_results['net_worth'][:, 0] * 2).mean(),
                '',
                '',
                export_income,
                export_expenses,
                export_liquid,
                export_property,
                export_mortgage
            ]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        worksheet = writer.sheets['Summary']
        worksheet.set_column('A:A', 35)
        worksheet.set_column('B:B', 20)
        
        # Add note about currency
        worksheet.write(15, 0, f'Note: All amounts in {selected_currency}', header_format)
        
        # Net Worth Projections
        percentiles_data = {
            'Year': years_array,
            '10th Percentile': np.percentile(export_results['net_worth'], 10, axis=0),
            '25th Percentile': np.percentile(export_results['net_worth'], 25, axis=0),
            '50th Percentile (Median)': np.percentile(export_results['net_worth'], 50, axis=0),
            '75th Percentile': np.percentile(export_results['net_worth'], 75, axis=0),
            '90th Percentile': np.percentile(export_results['net_worth'], 90, axis=0),
        }
        percentiles_df = pd.DataFrame(percentiles_data)
        percentiles_df.to_excel(writer, sheet_name='Net Worth Projections', index=False)
        
        # Wealth Components
        components_data = {
            'Year': years_array,
            'Liquid Wealth': np.median(export_results['liquid_wealth'], axis=0),
            'Pension Wealth': np.median(export_results['pension_wealth'], axis=0),
            'Property Value': np.median(export_results['property_value'], axis=0),
            'Mortgage Balance': np.median(export_results['mortgage_balance'], axis=0),
            'Property Equity': np.median(export_results['property_value'] - export_results['mortgage_balance'], axis=0),
            'Total Net Worth': np.median(export_results['net_worth'], axis=0)
        }
        components_df = pd.DataFrame(components_data)
        components_df['Currency'] = selected_currency  # Add currency column
        components_df.to_excel(writer, sheet_name='Wealth Components', index=False)
        
        # Events (if any)
        if export_events:
            events_data = []
            for event in export_events:
                event_row = {
                    'Year': event['year'],
                    'Type': event['type'].replace('_', ' ').title(),
                    'Description': event['name']
                }
                
                if event['type'] == 'property_purchase':
                    event_row['Details'] = f"Price: {format_currency(event['property_price'], selected_currency)}, Down: {format_currency(event['down_payment'], selected_currency)}"
                elif event['type'] == 'property_sale':
                    event_row['Details'] = f"Sale: {format_currency(event['sale_price'], selected_currency)}"
                elif event['type'] == 'one_time_expense':
                    event_row['Details'] = f"Expense: {format_currency(event['amount'], selected_currency)}"
                elif event['type'] == 'expense_change':
                    event_row['Details'] = f"Monthly Change: {format_currency(event['monthly_change'], selected_currency)}"
                elif event['type'] == 'rental_income':
                    event_row['Details'] = f"Monthly Rental: {format_currency(event['monthly_rental'], selected_currency)}"
                elif event['type'] == 'windfall':
                    event_row['Details'] = f"Amount: {format_currency(event['amount'], selected_currency)}"
                
                events_data.append(event_row)
            
            events_df = pd.DataFrame(events_data)
            events_df.to_excel(writer, sheet_name='Financial Events', index=False)
    
    output.seek(0)
    return output.getvalue()


def export_to_pdf(results, currency_symbol, selected_currency, events, fig_main, fig_composition,
                  gross_annual_income, monthly_expenses, initial_liquid_wealth,
                  initial_property_value, initial_mortgage):
    """Export simulation results to PDF file"""
    output = io.BytesIO()
    
    # ADD THESE LINES AT THE TOP:
    # Convert results and events for export
    export_results = convert_simulation_results_to_display(results, selected_currency)
    export_events = convert_events_from_base(events, selected_currency)
    
    # Convert input values for export
    export_income = from_base_currency(gross_annual_income, selected_currency)
    export_expenses = from_base_currency(monthly_expenses, selected_currency)
    export_liquid = from_base_currency(initial_liquid_wealth, selected_currency)
    export_property = from_base_currency(initial_property_value, selected_currency)
    export_mortgage = from_base_currency(initial_mortgage, selected_currency)
    
    # NOW USE export_results, export_events, and export_* values
    # Change all 'results' to 'export_results'
    # Change all input values to export_* versions
    
    doc = SimpleDocTemplate(output, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=HexColor('#2E7D32'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=HexColor('#1976D2'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    # Title with currency info
    story.append(Paragraph(f"Wealth Simulation Report", title_style))
    story.append(Paragraph(f"Currency: {selected_currency} (Base: {BASE_CURRENCY})", styles['Normal']))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Initial Inputs
    story.append(Paragraph("Initial Financial Position", heading_style))
    
    inputs_data = [
        ['Metric', 'Value'],
        ['Gross Annual Income', format_currency(export_income, selected_currency)],
        ['Monthly Expenses', format_currency(export_expenses, selected_currency)],
        ['Initial Liquid Wealth', format_currency(export_liquid, selected_currency)],
        ['Initial Property Value', format_currency(export_property, selected_currency)],
        ['Initial Mortgage', format_currency(export_mortgage, selected_currency)],
    ]
    
    inputs_table = Table(inputs_data, colWidths=[3*inch, 2*inch])
    inputs_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#4CAF50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), beige),
        ('GRID', (0, 0), (-1, -1), 1, black),
    ]))
    
    story.append(inputs_table)
    story.append(Spacer(1, 20))
    
    # Summary Statistics
    story.append(Paragraph("Summary Statistics", heading_style))
    
    summary_data = [
        ['Metric', 'Value'],
        ['Median Final Net Worth', format_currency(np.median(export_results['net_worth'][:, -1]), selected_currency)],
        ['Mean Final Net Worth', format_currency(np.mean(export_results['net_worth'][:, -1]), selected_currency)],
        ['10th Percentile', format_currency(np.percentile(export_results['net_worth'][:, -1], 10), selected_currency)],
        ['90th Percentile', format_currency(np.percentile(export_results['net_worth'][:, -1], 90), selected_currency)],
        ['Probability of Growth', f"{(export_results['net_worth'][:, -1] > export_results['net_worth'][:, 0]).mean() * 100:.1f}%"],
        ['Probability of 2x Growth', f"{(export_results['net_worth'][:, -1] > export_results['net_worth'][:, 0] * 2).mean() * 100:.1f}%"],
    ]
    
    summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#4CAF50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), beige),
        ('GRID', (0, 0), (-1, -1), 1, black),
    ]))
    
    story.append(summary_table)
    story.append(Spacer(1, 20))
    
    # Add currency conversion note
    story.append(Paragraph(
        f"Note: All monetary values are displayed in {selected_currency}. "
        f"Internal calculations use {BASE_CURRENCY} as the base currency.",
        styles['Normal']
    ))
    
    # Continue with charts and remaining content...
    # [Rest of PDF generation code remains similar]
    
    doc.build(story)
    output.seek(0)
    return output.getvalue()


# The rest of the code continues with the simulation function...
# [Keeping the existing Monte Carlo simulation function as-is since it works with base currency]


def export_to_pdf(results, currency_symbol, selected_currency, events, fig_main, fig_composition,
                  gross_annual_income, monthly_expenses, initial_liquid_wealth,
                  initial_property_value, initial_mortgage):
    """Export simulation results to PDF file"""
    output = io.BytesIO()
    
    doc = SimpleDocTemplate(output, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=HexColor('#2E7D32'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=HexColor('#1976D2'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    title = Paragraph("Wealth Simulation Report", title_style)
    story.append(title)
    
    date_text = f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}<br/>Currency: {selected_currency}"
    story.append(Paragraph(date_text, styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    story.append(Paragraph("Summary Statistics", heading_style))
    
    final_net_worth = display_results['net_worth'][:, -1]
    initial_net_worth = display_results['net_worth'][:, 0]
    
    summary_data = [
        ['Metric', 'Value'],
        ['Median Final Net Worth', format_currency(np.median(final_net_worth), selected_currency)],
        ['Mean Final Net Worth', format_currency(np.mean(final_net_worth), selected_currency)],
        ['10th Percentile', format_currency(np.percentile(final_net_worth, 10), selected_currency)],
        ['90th Percentile', format_currency(np.percentile(final_net_worth, 90), selected_currency)],
        ['Probability of Growth', f"{(final_net_worth > initial_net_worth).mean()*100:.1f}%"],
        ['Probability of 2x Growth', f"{(final_net_worth > initial_net_worth*2).mean()*100:.1f}%"],
    ]
    
    summary_table = Table(summary_data, colWidths=[3.5*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#4CAF50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), beige),
        ('GRID', (0, 0), (-1, -1), 1, black)
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 0.3*inch))
    
    story.append(Paragraph("Initial Position", heading_style))
    
    initial_data = [
        ['Component', 'Amount'],
        ['Liquid Wealth', format_currency(initial_liquid_wealth, selected_currency)],
        ['Property Value', format_currency(initial_property_value, selected_currency)],
        ['Mortgage Debt', format_currency(-initial_mortgage, selected_currency)],
        ['Net Worth', format_currency(initial_liquid_wealth + initial_property_value - initial_mortgage, selected_currency)],
        ['', ''],
        ['Gross Annual Income', format_currency(gross_annual_income, selected_currency)],
        ['Monthly Expenses', format_currency(monthly_expenses, selected_currency)],
    ]
    
    initial_table = Table(initial_data, colWidths=[3.5*inch, 2*inch])
    initial_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#4CAF50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), beige),
        ('GRID', (0, 0), (-1, -1), 1, black)
    ]))
    story.append(initial_table)
    
    if events:
        story.append(PageBreak())
        story.append(Paragraph("Configured Financial Events", heading_style))
        
        events_data = [['Year', 'Type', 'Description']]
        for event in events:
            events_data.append([
                str(event['year']),
                event['type'].replace('_', ' ').title(),
                event['name']
            ])
        
        events_table = Table(events_data, colWidths=[0.8*inch, 2*inch, 3*inch])
        events_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#4CAF50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), beige),
            ('GRID', (0, 0), (-1, -1), 1, black)
        ]))
        story.append(events_table)
    
    story.append(PageBreak())
    story.append(Paragraph("Net Worth Trajectory", heading_style))
    
    img_bytes = pio.to_image(fig_main, format='png', width=700, height=400)
    img = Image(io.BytesIO(img_bytes), width=6.5*inch, height=3.7*inch)
    story.append(img)
    
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("Wealth Composition", heading_style))
    
    img_bytes2 = pio.to_image(fig_composition, format='png', width=700, height=400)
    img2 = Image(io.BytesIO(img_bytes2), width=6.5*inch, height=3.7*inch)
    story.append(img2)
    
    story.append(PageBreak())
    story.append(Paragraph("Net Worth Percentiles by Year", heading_style))
    
    milestone_years = [5, 10, 15, 20, 25, 30]
    percentile_data = [['Year', '10th', '25th', '50th (Median)', '75th', '90th']]
    
    for year in milestone_years:
        if year < display_results['net_worth'].shape[1]:
            year_wealth = display_results['net_worth'][:, year]
            percentile_data.append([
                str(year),
                format_currency(np.percentile(year_wealth, 10), selected_currency),
                format_currency(np.percentile(year_wealth, 25), selected_currency),
                format_currency(np.percentile(year_wealth, 50), selected_currency),
                format_currency(np.percentile(year_wealth, 75), selected_currency),
                format_currency(np.percentile(year_wealth, 90), selected_currency),
            ])
    
    percentile_table = Table(percentile_data, colWidths=[0.6*inch, 1.1*inch, 1.1*inch, 1.2*inch, 1.1*inch, 1.1*inch])
    percentile_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#4CAF50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), beige),
        ('GRID', (0, 0), (-1, -1), 1, black),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
    ]))
    story.append(percentile_table)
    
    story.append(Spacer(1, 0.3*inch))
    disclaimer = Paragraph(
        "<i>Disclaimer: This report is for educational and planning purposes only. "
        "It is not financial advice. Past performance does not guarantee future results. "
        "Consult with a qualified financial advisor before making investment decisions.</i>",
        styles['Normal']
    )
    story.append(disclaimer)
    
    doc.build(story)
    output.seek(0)
    return output


def run_monte_carlo(initial_liquid_wealth, initial_property_value, initial_mortgage,
                    gross_annual_income, effective_tax_rate, pension_contribution_rate,
                    monthly_expenses, monthly_mortgage_payment,
                    property_appreciation, mortgage_interest_rate,
                    expected_return, return_volatility, expected_inflation, inflation_volatility,
                    salary_inflation, years, n_simulations, events, random_seed):
    """Run Monte Carlo simulation for wealth paths"""
    np.random.seed(random_seed)
    
    liquid_wealth_paths = np.zeros((n_simulations, years + 1))
    property_value_paths = np.zeros((n_simulations, years + 1))
    mortgage_balance_paths = np.zeros((n_simulations, years + 1))
    pension_wealth_paths = np.zeros((n_simulations, years + 1))
    
    monthly_expenses_tracker = np.full((n_simulations, years + 1), monthly_expenses, dtype=float)
    monthly_mortgage_tracker = np.full((n_simulations, years + 1), monthly_mortgage_payment, dtype=float)
    monthly_rental_tracker = np.zeros((n_simulations, years + 1))
    
    liquid_wealth_paths[:, 0] = initial_liquid_wealth
    property_value_paths[:, 0] = initial_property_value
    mortgage_balance_paths[:, 0] = initial_mortgage
    pension_wealth_paths[:, 0] = 0
    
    net_worth_paths = np.zeros((n_simulations, years + 1))
    net_worth_paths[:, 0] = initial_liquid_wealth + initial_property_value - initial_mortgage
    
    real_net_worth_paths = np.zeros((n_simulations, years + 1))
    real_net_worth_paths[:, 0] = net_worth_paths[:, 0]
    
    portfolio_returns = np.random.normal(expected_return, return_volatility, (n_simulations, years))
    pension_returns = np.random.normal(expected_return, return_volatility, (n_simulations, years))
    inflation_rates = np.random.normal(expected_inflation, inflation_volatility, (n_simulations, years))
    inflation_rates = np.maximum(inflation_rates, -0.05)
    
    events_by_year = {}
    for event in events:
        year = event['year']
        if year not in events_by_year:
            events_by_year[year] = []
        events_by_year[year].append(event)
    
    for year in range(1, years + 1):
        cumulative_inflation = np.prod(1 + inflation_rates[:, :year], axis=1)
        cumulative_salary_growth = (1 + salary_inflation) ** year
        
        current_monthly_expenses = monthly_expenses_tracker[:, year - 1]
        current_monthly_mortgage = monthly_mortgage_tracker[:, year - 1]
        current_monthly_rental = monthly_rental_tracker[:, year - 1]
        
        year_gross_income = gross_annual_income * cumulative_salary_growth
        year_pension_contribution = year_gross_income * pension_contribution_rate
        year_take_home = year_gross_income * (1 - effective_tax_rate - pension_contribution_rate)
        year_expenses = current_monthly_expenses * 12 * cumulative_inflation
        year_mortgage_payment = current_monthly_mortgage * 12
        year_rental_income = current_monthly_rental * 12 * cumulative_inflation
        
        year_available_savings = year_take_home + year_rental_income - year_expenses - year_mortgage_payment
        
        pension_wealth_paths[:, year] = (
            pension_wealth_paths[:, year - 1] * (1 + pension_returns[:, year - 1]) +
            year_pension_contribution
        )
        
        liquid_wealth_paths[:, year] = (
            liquid_wealth_paths[:, year - 1] * (1 + portfolio_returns[:, year - 1]) +
            year_available_savings
        )
        
        property_value_paths[:, year] = (
            property_value_paths[:, year - 1] * (1 + property_appreciation)
        )
        
        if mortgage_balance_paths[:, year - 1].mean() > 0:
            year_interest = mortgage_balance_paths[:, year - 1] * mortgage_interest_rate
            year_principal = np.maximum(year_mortgage_payment - year_interest, 0)
            mortgage_balance_paths[:, year] = np.maximum(
                mortgage_balance_paths[:, year - 1] - year_principal, 0
            )
        else:
            mortgage_balance_paths[:, year] = 0
        
        if year in events_by_year:
            for event in events_by_year[year]:
                if event['type'] == 'property_purchase':
                    liquid_wealth_paths[:, year] -= event['down_payment']
                    property_value_paths[:, year] += event['property_price']
                    mortgage_balance_paths[:, year] += event['mortgage_amount']
                    monthly_mortgage_tracker[:, year:] = event['new_mortgage_payment']
                    
                elif event['type'] == 'property_sale':
                    net_proceeds = (event['sale_price'] - event['mortgage_payoff'] - event['selling_costs'])
                    liquid_wealth_paths[:, year] += net_proceeds
                    property_value_paths[:, year] = 0
                    mortgage_balance_paths[:, year] = np.maximum(
                        mortgage_balance_paths[:, year] - event['mortgage_payoff'], 0
                    )
                    if event['mortgage_payoff'] >= mortgage_balance_paths[:, year].mean():
                        monthly_mortgage_tracker[:, year:] = 0
                    
                elif event['type'] == 'one_time_expense':
                    liquid_wealth_paths[:, year] -= event['amount']
                    
                elif event['type'] == 'expense_change':
                    monthly_expenses_tracker[:, year:] += event['monthly_change']
                    
                elif event['type'] == 'rental_income':
                    monthly_rental_tracker[:, year:] += event['monthly_rental']
                    
                elif event['type'] == 'windfall':
                    liquid_wealth_paths[:, year] += event['amount']
        
        net_worth_paths[:, year] = (
            liquid_wealth_paths[:, year] +
            pension_wealth_paths[:, year] +
            property_value_paths[:, year] -
            mortgage_balance_paths[:, year]
        )
        
        real_net_worth_paths[:, year] = net_worth_paths[:, year] / cumulative_inflation
    
    return {
        'net_worth': net_worth_paths,
        'real_net_worth': real_net_worth_paths,
        'liquid_wealth': liquid_wealth_paths,
        'pension_wealth': pension_wealth_paths,
        'property_value': property_value_paths,
        'mortgage_balance': mortgage_balance_paths,
        'inflation_rates': inflation_rates
    }


# Helper function to calculate mortgage payment
def calculate_mortgage_payment(principal, annual_rate, years):
    """Calculate monthly mortgage payment"""
    if principal <= 0 or years <= 0:
        return 0
    monthly_rate = annual_rate / 12
    n_payments = years * 12
    if monthly_rate > 0:
        payment = principal * (monthly_rate * (1 + monthly_rate)**n_payments) / ((1 + monthly_rate)**n_payments - 1)
    else:
        payment = principal / n_payments
    return payment


# Create tabs with session state control
# Check if we should switch to simulation tab
if st.session_state.get('switch_to_simulation', False):
    # Clear the flag
    st.session_state.switch_to_simulation = False
    # Set default tab to simulation
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = 0
    st.session_state.active_tab = 0

# Initialize active tab if not set
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = 0

# Create tabs - note: we can't programmatically select, but we can reorder content
# Workaround: Use radio buttons styled as tabs or show info message
tab1, tab2 = st.tabs(["🎲 Simulation", "💰 Budget Builder"])

# Show message if user just came from budget builder
if st.session_state.get('just_set_budget', False):
    st.info("✅ Budget loaded! You're now on the Simulation tab.")
    st.session_state.just_set_budget = False

with tab2:
    from budget_builder import show_budget_builder
    show_budget_builder()

with tab1:
    # Initialize session state for budget integration
    if 'budget_monthly_expenses' not in st.session_state:
        st.session_state.budget_monthly_expenses = None
    if 'budget_events_list' not in st.session_state:
        st.session_state.budget_events_list = []
    if 'budget_currency' not in st.session_state:
        st.session_state.budget_currency = 'EUR'  # Default to EUR if not set
    if 'selected_currency' not in st.session_state:
        st.session_state.selected_currency = 'EUR'
    
    # Initialize display values for currency conversion
    if 'display_liquid_wealth' not in st.session_state:
        st.session_state.display_liquid_wealth = 50000
    if 'display_property_value' not in st.session_state:
        st.session_state.display_property_value = 0
    if 'display_mortgage' not in st.session_state:
        st.session_state.display_mortgage = 0
    if 'display_annual_income' not in st.session_state:
        st.session_state.display_annual_income = 60000
    if 'display_monthly_expenses' not in st.session_state:
        st.session_state.display_monthly_expenses = 2500


    # Title
    st.title("30-Year Wealth Path Simulator")
    st.markdown("Interactive Monte Carlo simulation to explore your financial future")
    
    # Show loaded simulation indicator
    if st.session_state.get('loaded_simulation_name'):
        st.info(f"📂 Currently viewing: **{st.session_state.loaded_simulation_name}**")

    # Save/Load Simulation Controls
    if st.session_state.get('authenticated', False):
        with st.expander("💾 Save / Load Simulations", expanded=False):
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("📥 Load Simulation")
                
                # Get user's saved simulations
                user_sims = get_user_simulations(st.session_state.user_id, limit=20)
                
                if user_sims:
                    sim_options = {f"{sim.name} ({sim.created_at.strftime('%Y-%m-%d %H:%M')})": sim.id for sim in user_sims}
                    
                    selected_sim_name = st.selectbox(
                        "Select a saved simulation",
                        options=[""] + list(sim_options.keys()),
                        key="load_sim_selector"
                    )
                    
                    col_load, col_delete = st.columns([1, 1])
                    
                    with col_load:
                        if st.button("Load", type="primary", disabled=not selected_sim_name, use_container_width=True):
                            if selected_sim_name:
                                sim_id = sim_options[selected_sim_name]
                                success, data = load_simulation(sim_id, st.session_state.user_id)
                                
                                if success:
                                    state = data['state']
                                    
                                    # Restore all session state variables
                                    if 'parameters' in state:
                                        params = state['parameters']
                                        
                                        # Restore base currency values
                                        st.session_state.base_liquid_wealth = params.get('initial_liquid_wealth', 50000)
                                        st.session_state.base_property_value = params.get('initial_property_value', 0)
                                        st.session_state.base_mortgage = params.get('initial_mortgage', 0)
                                        st.session_state.base_annual_income = params.get('gross_annual_income', 60000)
                                        st.session_state.base_monthly_expenses = params.get('monthly_expenses', 2500)
                                        
                                        # Restore currency
                                        st.session_state.selected_currency = params.get('currency', 'EUR')
                                        
                                        # Restore age settings
                                        if 'starting_age' in params:
                                            st.session_state.current_age = params['starting_age']
                                        if 'retirement_age' in params:
                                            st.session_state.target_retirement_age = params['retirement_age']
                                        
                                        # Restore budget integration if available
                                        if 'budget_monthly_expenses' in params:
                                            st.session_state.budget_monthly_expenses = params['budget_monthly_expenses']
                                        if 'budget_events_list' in params:
                                            st.session_state.budget_events_list = params['budget_events_list']
                                        if 'use_budget_builder' in params:
                                            st.session_state.use_budget_builder = params['use_budget_builder']
                                    
                                    # Restore results if available
                                    if 'results_data' in state:
                                        # Convert lists back to numpy arrays
                                        results_data = state['results_data']
                                        restored_results = {}
                                        for key, value in results_data.items():
                                            if isinstance(value, list):
                                                restored_results[key] = np.array(value)
                                            else:
                                                restored_results[key] = value
                                        
                                        st.session_state.results = restored_results
                                        st.session_state.sim_complete = True
                                        st.session_state.starting_age = state['parameters'].get('starting_age', 30)
                                        st.session_state.retirement_age = state['parameters'].get('retirement_age', 65)
                                        st.session_state.simulation_years = state['parameters'].get('simulation_years', 35)
                                        st.session_state.base_events = state['parameters'].get('events', [])
                                        st.session_state.monthly_mortgage_payment = state['parameters'].get('monthly_mortgage_payment', 0)
                                    
                                    # Set indicator for loaded simulation
                                    st.session_state.loaded_simulation_name = data['name']
                                    st.session_state.loaded_simulation_id = sim_id
                                    
                                    st.success(f"✅ Loaded: {data['name']}")
                                    st.rerun()
                                else:
                                    st.error(f"❌ {data}")
                    
                    with col_delete:
                        if st.button("Delete", type="secondary", disabled=not selected_sim_name, use_container_width=True):
                            if selected_sim_name:
                                sim_id = sim_options[selected_sim_name]
                                success, message = delete_simulation(sim_id, st.session_state.user_id)
                                if success:
                                    st.success(f"✅ {message}")
                                    st.rerun()
                                else:
                                    st.error(f"❌ {message}")
                else:
                    st.info("No saved simulations yet. Run a simulation and save it!")
            
            with col2:
                st.subheader("💾 Save Current Simulation")
                
                if st.session_state.get('sim_complete', False):
                    save_name = st.text_input(
                        "Simulation Name",
                        value=f"Simulation {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                        key="save_sim_name"
                    )
                    
                    if st.button("Save Simulation", type="primary", use_container_width=True):
                        # Gather all current state
                        results = st.session_state.get('results', {})
                        
                        # Convert numpy arrays to lists for JSON serialization
                        results_data = {}
                        for key, value in results.items():
                            if isinstance(value, np.ndarray):
                                results_data[key] = value.tolist()
                            else:
                                results_data[key] = value
                        
                        # Calculate summary statistics
                        final_median_net_worth = float(np.median(results['net_worth'][:, -1])) if 'net_worth' in results else 0
                        initial_net_worth = results['net_worth'][:, 0] if 'net_worth' in results else np.array([0])
                        final_values = results['net_worth'][:, -1] if 'net_worth' in results else np.array([0])
                        probability_of_success = float((final_values > initial_net_worth[0]).mean()) if len(final_values) > 0 else 0
                        
                        simulation_state = {
                            'parameters': {
                                'name': save_name,
                                'currency': st.session_state.get('selected_currency', 'EUR'),
                                'initial_liquid_wealth': st.session_state.get('base_liquid_wealth', 50000),
                                'initial_property_value': st.session_state.get('base_property_value', 0),
                                'initial_mortgage': st.session_state.get('base_mortgage', 0),
                                'gross_annual_income': st.session_state.get('base_annual_income', 60000),
                                'monthly_expenses': st.session_state.get('base_monthly_expenses', 2500),
                                'events': st.session_state.get('base_events', []),
                                'starting_age': st.session_state.get('starting_age', 30),
                                'retirement_age': st.session_state.get('retirement_age', 65),
                                'simulation_years': st.session_state.get('simulation_years', 35),
                                'budget_monthly_expenses': st.session_state.get('budget_monthly_expenses'),
                                'budget_events_list': st.session_state.get('budget_events_list', []),
                                'use_budget_builder': st.session_state.get('use_budget_builder', False),
                            },
                            'results_data': results_data,
                            'results': {
                                'final_median_net_worth': final_median_net_worth,
                                'probability_of_success': probability_of_success,
                            }
                        }
                        
                        success, result = save_full_simulation(
                            st.session_state.user_id,
                            save_name,
                            simulation_state
                        )
                        
                        if success:
                            st.success(f"✅ Saved as: {save_name}")
                        else:
                            st.error(f"❌ Error: {result}")
                else:
                    st.info("Run a simulation first to save it")

    # ============================================================================
    # ALL SIDEBAR CONTROLS
    # ============================================================================

    # Admin Analytics Access (for developers)
    admin_users = ['admin', 'nbourke']  # Add your admin usernames here
    if st.session_state.get('username') in admin_users:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🔧 Developer Tools")
        if st.sidebar.button("📊 Admin Analytics Dashboard"):
            # Import and run admin analytics module directly
            import importlib.util
            spec = importlib.util.spec_from_file_location("admin_analytics", "admin_analytics.py")
            admin_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(admin_module)
            st.stop()
        st.sidebar.markdown("---")

    st.sidebar.header("⚙️ Settings")
    
    # Age settings
    if st.session_state.get('authenticated', False):
        default_current_age = st.session_state.get('current_age', 30)
        default_retirement_age = st.session_state.get('target_retirement_age', 65)
    else:
        default_current_age = 30
        default_retirement_age = 65
    
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        starting_age = st.number_input(
            "Starting Age",
            min_value=18,
            max_value=100,
            value=default_current_age,
            step=1,
            help="Age to start simulation from"
        )
    
    with col2:
        retirement_age = st.number_input(
            "Retirement Age",
            min_value=starting_age + 1,
            max_value=100,
            value=default_retirement_age,
            step=1,
            help="Target retirement age"
        )
    
    simulation_years = retirement_age - starting_age
    st.sidebar.info(f"Simulating **{simulation_years} years** (Age {starting_age} → {retirement_age})")
    
    if simulation_years <= 0:
        st.sidebar.error("⚠️ Retirement age must be greater than starting age")
        st.stop()
    
    st.sidebar.markdown("---")

    # Currency Selector - SIMPLIFIED VERSION
    st.sidebar.header("💱 Currency")

    previous_currency = st.session_state.get('selected_currency', BASE_CURRENCY)

    selected_currency = st.sidebar.selectbox(
        "Currency",
        options=list(CURRENCIES.keys()),
        format_func=lambda x: f"{CURRENCIES[x]['symbol']} {CURRENCIES[x]['name']} ({x})",
        index=list(CURRENCIES.keys()).index(previous_currency),
        key="currency_selector"
    )

    # Handle currency change
    if selected_currency != previous_currency:
        handle_currency_change(previous_currency, selected_currency)
        
        # Clear old manual event widget keys (they don't have currency suffix)
        old_keys = [k for k in st.session_state.keys() if k.startswith('manual_') and not k.endswith(f'_{selected_currency}')]
        for key in old_keys:
            del st.session_state[key]

    st.session_state.selected_currency = selected_currency
    currency_symbol = CURRENCIES[selected_currency]['symbol']

    # Show currency info
    create_currency_info_widget()



    # Initial Position
    st.sidebar.header("Initial Position")

    display_liquid = get_display_value('base_liquid_wealth', selected_currency)

    initial_liquid_wealth = st.sidebar.number_input(
        f"Initial Liquid Wealth ({currency_symbol})",
        min_value=0,
        value=int(display_liquid),
        step=10000,
        key=f'widget_liquid_wealth_{selected_currency}'
    )

    st.session_state.base_liquid_wealth = to_base_currency(
        initial_liquid_wealth,
        selected_currency
    )

    display_property = get_display_value('base_property_value', selected_currency)

    initial_property_value = st.sidebar.number_input(
        f"Initial Property Value ({currency_symbol})",
        min_value=0,
        value=int(display_property),
        step=25000,
        key=f'widget_property_value_{selected_currency}'
    )

    st.session_state.base_property_value = to_base_currency(
        initial_property_value,
        selected_currency
    )

    display_mortgage = get_display_value('base_mortgage', selected_currency)

    initial_mortgage = st.sidebar.number_input(
        f"Initial Mortgage Balance ({currency_symbol})",
        min_value=0,
        value=int(display_mortgage),
        step=25000,
        key=f'widget_mortgage_{selected_currency}'
    )

    st.session_state.base_mortgage = to_base_currency(
        initial_mortgage,
        selected_currency
    )

    initial_mortgage_amortization = st.sidebar.number_input(
        "Initial Mortgage Amortization (years)",
        min_value=0,
        max_value=35,
        value=25,
        step=1
    )

    mortgage_interest_rate = st.sidebar.slider(
        "Mortgage Interest Rate (%)",
        min_value=0.0,
        max_value=10.0,
        value=3.5,
        step=0.25
    ) / 100

    # Calculate initial monthly mortgage payment using base currency
    base_mortgage = st.session_state.base_mortgage
    if base_mortgage > 0 and initial_mortgage_amortization > 0:
        monthly_rate = mortgage_interest_rate / 12
        n_payments = initial_mortgage_amortization * 12
        if monthly_rate > 0:
            calculated_payment = base_mortgage * (monthly_rate * (1 + monthly_rate)**n_payments) / ((1 + monthly_rate)**n_payments - 1)
        else:
            calculated_payment = base_mortgage / n_payments
    else:
        calculated_payment = 0

    st.sidebar.markdown("---")

    # Income & Tax
    st.sidebar.header("Income & Tax")

    display_income = get_display_value('base_annual_income', selected_currency)

    gross_annual_income = st.sidebar.number_input(
        f"Gross Annual Income ({currency_symbol})",
        min_value=0,
        value=int(display_income),
        step=5000,
        key=f'widget_annual_income_{selected_currency}'
    )

    st.session_state.base_annual_income = to_base_currency(
        gross_annual_income,
        selected_currency
    )


    effective_tax_rate = st.sidebar.slider(
        "Effective Tax Rate (%)",
        min_value=0.0,
        max_value=50.0,
        value=25.0,
        step=1.0
    ) / 100

    pension_contribution_rate = st.sidebar.slider(
        "Pension Contribution (% of gross)",
        min_value=0.0,
        max_value=30.0,
        value=10.0,
        step=1.0
    ) / 100

    # Monthly Budget
    st.sidebar.header("Monthly Budget")

    # Get display value from base
    display_expenses = get_display_value('base_monthly_expenses', selected_currency)

    # Handle budget builder integration - OVERRIDE display_expenses if budget is active
    if st.session_state.get('use_budget_builder', False):
        budget_value = st.session_state.get('budget_monthly_expenses', None)
        if budget_value is not None and budget_value > 0:
            # Convert budget value to base using the currency it was created in
            budget_currency = st.session_state.get('budget_currency', 'EUR')
            base_budget = to_base_currency(budget_value, budget_currency)
            st.session_state.base_monthly_expenses = base_budget
            display_expenses = from_base_currency(base_budget, selected_currency)
            
            # Force update the widget's session state so it shows the correct value
            widget_key = f'widget_monthly_expenses_{selected_currency}'
            st.session_state[widget_key] = int(display_expenses)
            
            st.sidebar.success(f"💡 Using Budget Builder: {format_currency(display_expenses, selected_currency)}")

    monthly_expenses = st.sidebar.number_input(
        f"Monthly Living Expenses ({currency_symbol})",
        min_value=0,
        value=int(display_expenses),
        step=250,
        key=f'widget_monthly_expenses_{selected_currency}'
    )

    # Only update base if NOT using budget builder (budget already set it above)
    if not st.session_state.get('use_budget_builder', False):
        st.session_state.base_monthly_expenses = to_base_currency(
            monthly_expenses,
            selected_currency
        )

    st.sidebar.markdown("---")

    # Property Assumptions
    st.sidebar.header("Property Assumptions")

    property_appreciation = st.sidebar.slider(
        "Annual Property Appreciation (%)",
        min_value=-5.0,
        max_value=15.0,
        value=3.0,
        step=0.5
    ) / 100

    # Investment
    st.sidebar.subheader("Investment Assumptions")

    expected_return = st.sidebar.slider(
        "Expected Annual Return (%)",
        min_value=0.0,
        max_value=15.0,
        value=7.0,
        step=0.5
    ) / 100

    return_volatility = st.sidebar.slider(
        "Return Volatility (Std Dev %)",
        min_value=0.0,
        max_value=30.0,
        value=15.0,
        step=1.0
    ) / 100

    # Inflation
    st.sidebar.subheader("Inflation")

    expected_inflation = st.sidebar.slider(
        "Expected Inflation (%)",
        min_value=0.0,
        max_value=10.0,
        value=2.5,
        step=0.25
    ) / 100

    inflation_volatility = st.sidebar.slider(
        "Inflation Volatility (Std Dev %)",
        min_value=0.0,
        max_value=5.0,
        value=1.0,
        step=0.25
    ) / 100

    salary_inflation = st.sidebar.slider(
        "Salary Inflation (%)",
        min_value=0.0,
        max_value=10.0,
        value=2.5,
        step=0.25
    ) / 100

    st.sidebar.markdown("---")

    # Simulation Settings
    st.sidebar.subheader("Simulation Settings")

    n_simulations = st.sidebar.select_slider(
        "Number of Simulations",
        options=[100, 500, 1000, 2000, 5000],
        value=1000
    )

    random_seed = st.sidebar.number_input(
        "Random Seed",
        min_value=0,
        value=42,
        step=1
    )

    st.sidebar.markdown("---")

    # Major Financial Events
    st.sidebar.subheader("Major Financial Events")

    events = []
    budget_events_list = st.session_state.get('budget_events_list', [])

    # Helper function to convert event monetary values to base currency
    def convert_event_value_to_base(value, event_currency='EUR'):
        """Convert a monetary value from event's currency to base currency (EUR)"""
        if event_currency == 'EUR':
            return value
        return to_base_currency(value, event_currency)

    if budget_events_list:
        use_budget_events = st.sidebar.checkbox(
            f"✨ Use {len(budget_events_list)} events from Budget Builder",
            value=True
        )
        
        if use_budget_events:
            st.sidebar.success(f"✅ Using {len(budget_events_list)} Budget Builder events")
            
            with st.sidebar.expander("📋 View Budget Events"):
                for evt in budget_events_list:
                    st.write(f"**Year {evt['year']}:** {evt['name']}")
            
            for budget_event in budget_events_list:
                event_type = budget_event['simulation_type']
                year = budget_event['year']
                name = budget_event['name']
                details = budget_event.get('details', {})
                event_currency = budget_event.get('currency', 'EUR')  # Get event's currency
                
                if event_type == 'property_purchase':
                    mortgage_amount = convert_event_value_to_base(
                        details.get('mortgage_amount', 400000),
                        event_currency
                    )
                    new_payment = calculate_mortgage_payment(
                        mortgage_amount,
                        mortgage_interest_rate,
                        details.get('mortgage_years', 25)
                    )
                    events.append({
                        'type': 'property_purchase',
                        'year': year,
                        'name': name,
                        'from_budget': True,  # Mark as budget event (already converted)
                        'property_price': convert_event_value_to_base(
                            details.get('property_price', 500000),
                            event_currency
                        ),
                        'down_payment': convert_event_value_to_base(
                            details.get('down_payment', 100000),
                            event_currency
                        ),
                        'mortgage_amount': mortgage_amount,
                        'new_mortgage_payment': calculated_payment + new_payment
                    })
                
                elif event_type == 'property_sale':
                    events.append({
                        'type': 'property_sale',
                        'year': year,
                        'name': name,
                        'from_budget': True,
                        'sale_price': convert_event_value_to_base(
                            details.get('sale_price', 600000),
                            event_currency
                        ),
                        'mortgage_payoff': convert_event_value_to_base(
                            details.get('mortgage_payoff', 350000),
                            event_currency
                        ),
                        'selling_costs': convert_event_value_to_base(
                            details.get('selling_costs', 30000),
                            event_currency
                        )
                    })
                
                elif event_type == 'one_time_expense':
                    events.append({
                        'type': 'one_time_expense',
                        'year': year,
                        'name': name,
                        'from_budget': True,
                        'amount': convert_event_value_to_base(
                            details.get('amount', 30000),
                            event_currency
                        )
                    })
                
                elif event_type == 'expense_change':
                    monthly_change = details.get('monthly_change')
                    if monthly_change is None:
                        monthly_change = sum(budget_event['impacts']['changes'].values())
                    
                    events.append({
                        'type': 'expense_change',
                        'year': year,
                        'name': name,
                        'from_budget': True,
                        'monthly_change': convert_event_value_to_base(
                            monthly_change,
                            event_currency
                        )
                    })
                    
                    if budget_event['impacts']['one_time_costs'] > 0:
                        events.append({
                            'type': 'one_time_expense',
                            'year': year,
                            'name': f"{name} - Initial Costs",
                            'from_budget': True,
                            'amount': convert_event_value_to_base(
                                budget_event['impacts']['one_time_costs'],
                                event_currency
                            )
                        })
                
                elif event_type == 'rental_income':
                    events.append({
                        'type': 'rental_income',
                        'year': year,
                        'name': name,
                        'from_budget': True,
                        'monthly_rental': convert_event_value_to_base(
                            details.get('monthly_rental', 2000),
                            event_currency
                        )
                    })
                
                elif event_type == 'windfall':
                    events.append({
                        'type': 'windfall',
                        'year': year,
                        'name': name,
                        'from_budget': True,
                        'amount': convert_event_value_to_base(
                            details.get('amount', 50000),
                            event_currency
                        )
                    })

    # Manual events
    n_events = st.sidebar.number_input(
        "Additional Manual Events" if budget_events_list else "Number of Events",
        min_value=0,
        max_value=15,
        value=0,
        step=1
    )

    for i in range(n_events):
        with st.sidebar.expander(f"Manual Event {i+1}"):
            event_type = st.selectbox(
                "Type",
                ["Property Purchase", "Property Sale", "One-Time Expense", 
                 "Expense Change", "Rental Income", "Windfall"],
                key=f"manual_type_{i}"
            )
            
            event_year = st.number_input(
                "Year",
                min_value=0,
                max_value=simulation_years,
                value=5,
                key=f"manual_year_{i}"
            )
            
            event_name = st.text_input(
                "Name",
                value=f"{event_type} {i+1}",
                key=f"manual_name_{i}"
            )
            
            if event_type == "Property Purchase":
                prop_price = st.number_input(
                    f"Property Price ({currency_symbol})",
                    min_value=0,
                    value=500000,
                    step=25000,
                    key=f"manual_prop_price_{i}_{selected_currency}"
                )
                down_payment = st.number_input(
                    f"Down Payment ({currency_symbol})",
                    min_value=0,
                    value=100000,
                    step=10000,
                    key=f"manual_down_{i}_{selected_currency}"
                )
                mort_amount = st.number_input(
                    f"Mortgage Amount ({currency_symbol})",
                    min_value=0,
                    value=400000,
                    step=25000,
                    key=f"manual_mort_{i}_{selected_currency}"
                )
                mort_years = st.number_input(
                    "Mortgage Years",
                    min_value=1,
                    max_value=35,
                    value=25,
                    key=f"manual_mort_yrs_{i}"
                )
                
                new_payment = calculate_mortgage_payment(mort_amount, mortgage_interest_rate, mort_years)
                # Convert new_payment to base currency before adding to calculated_payment
                new_payment_base = to_base_currency(new_payment, selected_currency)
                events.append({
                    'type': 'property_purchase',
                    'year': event_year,
                    'name': event_name,
                    'property_price': prop_price,
                    'down_payment': down_payment,
                    'mortgage_amount': mort_amount,
                    'new_mortgage_payment': calculated_payment + new_payment_base
                })
            
            elif event_type == "Property Sale":
                sale_price = st.number_input(
                    f"Sale Price ({currency_symbol})",
                    min_value=0,
                    value=600000,
                    step=25000,
                    key=f"manual_sale_{i}_{selected_currency}"
                )
                payoff = st.number_input(
                    f"Mortgage Payoff ({currency_symbol})",
                    min_value=0,
                    value=350000,
                    step=25000,
                    key=f"manual_payoff_{i}_{selected_currency}"
                )
                costs = st.number_input(
                    f"Selling Costs ({currency_symbol})",
                    min_value=0,
                    value=30000,
                    step=5000,
                    key=f"manual_costs_{i}_{selected_currency}"
                )
                
                events.append({
                    'type': 'property_sale',
                    'year': event_year,
                    'name': event_name,
                    'sale_price': sale_price,
                    'mortgage_payoff': payoff,
                    'selling_costs': costs
                })
            
            elif event_type == "One-Time Expense":
                amount = st.number_input(
                    f"Amount ({currency_symbol})",
                    min_value=0,
                    value=30000,
                    step=5000,
                    key=f"manual_expense_{i}_{selected_currency}"
                )
                
                events.append({
                    'type': 'one_time_expense',
                    'year': event_year,
                    'name': event_name,
                    'amount': amount
                })
            
            elif event_type == "Expense Change":
                change = st.number_input(
                    f"Monthly Change ({currency_symbol})",
                    value=1000,
                    step=100,
                    key=f"manual_change_{i}_{selected_currency}"
                )
                
                events.append({
                    'type': 'expense_change',
                    'year': event_year,
                    'name': event_name,
                    'monthly_change': change
                })
            
            elif event_type == "Rental Income":
                rental = st.number_input(
                    f"Monthly Rental ({currency_symbol})",
                    min_value=0,
                    value=2000,
                    step=100,
                    key=f"manual_rental_{i}_{selected_currency}"
                )
                
                events.append({
                    'type': 'rental_income',
                    'year': event_year,
                    'name': event_name,
                    'monthly_rental': rental
                })
            
            elif event_type == "Windfall":
                amount = st.number_input(
                    f"Amount ({currency_symbol})",
                    min_value=0,
                    value=50000,
                    step=10000,
                    key=f"manual_windfall_{i}_{selected_currency}"
                )
                
                events.append({
                    'type': 'windfall',
                    'year': event_year,
                    'name': event_name,
                    'amount': amount
                })

    # Usage limits
    if st.session_state.get('authenticated', False):
        # Check if user is admin
        is_admin = st.session_state.get('username') in admin_users
        can_simulate, remaining, message = check_simulation_limit(
            st.session_state.user_id, 
            limit=5,  # Standard users get 5 simulations
            is_admin=is_admin
        )
    else:
        can_simulate = True
        message = "✓ Ready to simulate"

    st.sidebar.markdown("---")
    if not can_simulate:
        st.sidebar.error(message)
        # Show "Request More Simulations" button when limit reached
        if st.sidebar.button("🔄 Request More Simulations", type="secondary", use_container_width=True):
            success, reset_message = reset_simulation_count(st.session_state.user_id)
            if success:
                st.sidebar.success(reset_message)
                st.rerun()
            else:
                st.sidebar.error(reset_message)
    else:
        st.sidebar.success(message)

    # RUN SIMULATION BUTTON
    if st.sidebar.button("🚀 Run Simulation", type="primary", disabled=not can_simulate, use_container_width=True):
        # Clear loaded simulation indicator when running a new simulation
        if 'loaded_simulation_name' in st.session_state:
            del st.session_state.loaded_simulation_name
        if 'loaded_simulation_id' in st.session_state:
            del st.session_state.loaded_simulation_id
            
        with st.spinner(f"Running {simulation_years}-year simulation..."):
            # Use base currency values for simulation
            sim_liquid_wealth = st.session_state.base_liquid_wealth
            sim_property_value = st.session_state.base_property_value
            sim_mortgage = st.session_state.base_mortgage
            sim_income = st.session_state.base_annual_income
            sim_expenses = st.session_state.base_monthly_expenses
            
            # Budget events are already in base currency (converted when created)
            # Manual events need to be converted from display currency to base
            # Separate them to avoid double conversion
            budget_events = [e for e in events if 'from_budget' in e]
            manual_events = [e for e in events if 'from_budget' not in e]
            
            # Only convert manual events (budget events already converted)
            converted_manual_events = convert_events_to_base(manual_events, selected_currency) if manual_events else []
            
            # Combine both event types
            base_events = budget_events + converted_manual_events

            results = run_monte_carlo(
                initial_liquid_wealth=sim_liquid_wealth,
                initial_property_value=sim_property_value,
                initial_mortgage=sim_mortgage,
                gross_annual_income=sim_income,
                effective_tax_rate=effective_tax_rate,
                pension_contribution_rate=pension_contribution_rate,
                monthly_expenses=sim_expenses,
                monthly_mortgage_payment=calculated_payment,
                property_appreciation=property_appreciation,
                mortgage_interest_rate=mortgage_interest_rate,
                expected_return=expected_return,
                return_volatility=return_volatility,
                expected_inflation=expected_inflation,
                inflation_volatility=inflation_volatility,
                salary_inflation=salary_inflation,
                years=simulation_years,
                n_simulations=n_simulations,
                events=base_events,
                random_seed=random_seed
            )
            
            st.session_state['results'] = results
            st.session_state['sim_complete'] = True
            st.session_state['starting_age'] = starting_age
            st.session_state['retirement_age'] = retirement_age
            st.session_state['simulation_years'] = simulation_years
            st.session_state['base_events'] = base_events
            st.session_state['monthly_mortgage_payment'] = calculated_payment
            
            if st.session_state.get('authenticated', False):
                increment_simulation_count(st.session_state.user_id)
                
                simulation_params = {
                    'name': f"Simulation {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                    'currency': selected_currency,
                    'initial_liquid_wealth': initial_liquid_wealth,
                    'initial_property_value': initial_property_value,
                    'initial_mortgage': initial_mortgage,
                    'gross_annual_income': gross_annual_income,
                    'monthly_expenses': monthly_expenses,
                    'events': events,
                    'expected_return': expected_return,
                    'expected_inflation': expected_inflation,
                    'starting_age': starting_age,
                    'retirement_age': retirement_age,
                    'simulation_years': simulation_years,
                }
                
                save_simulation(st.session_state.user_id, simulation_params, results)
            
            st.success(f"✅ Simulation complete! Projected from age {starting_age} to {retirement_age}.")

    # Support/Donation Section
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💝 Support FinSim")
    st.sidebar.markdown("""
        Love FinSim? Help keep it **free** and **ad-free** for everyone!
        
        Your support helps us:
        - 🚀 Add new features
        - 🎨 Improve the user experience
        - 💾 Keep servers running
    """)
    
    # Ko-fi button with custom styling
    st.sidebar.markdown("""
        <a href="https://ko-fi.com/nialljb" target="_blank">
            <img src="https://ko-fi.com/img/githubbutton_sm.svg" 
                 alt="Support on Ko-fi" 
                 style="height: 36px; border: 0px;">
        </a>
    """, unsafe_allow_html=True)
    
    st.sidebar.caption("💡 Every coffee helps us improve FinSim!")

    # ============================================================================
    # DISPLAY RESULTS
    # ============================================================================

    if st.session_state.get('sim_complete', False):
        results = st.session_state['results']
        starting_age = st.session_state.get('starting_age', 30)
        retirement_age = st.session_state.get('retirement_age', 65)
        simulation_years = st.session_state.get('simulation_years', 30)
        
        # Get number of simulations from results array
        n_simulations = results['net_worth'].shape[0] if 'net_worth' in results else 1000
        
        display_results = convert_simulation_results_to_display(results, selected_currency)
        base_events = st.session_state.get('base_events', [])

        # Toggle controls
        col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
        with col1:
            show_real = st.checkbox("Show Real (Inflation-Adjusted)", value=True)
        with col2:
            view_type = st.selectbox(
                "View",
                ["Total Net Worth", "Liquid Wealth", "Property Equity", "Pension Wealth"]
            )
        with col3:
            show_conversion = st.checkbox("Show EUR Equivalent", value=False, 
                                         help="Display amounts in EUR for comparison")
        with col4:
            if show_conversion and selected_currency != 'EUR':
                rates = get_exchange_rates()
                rate = rates.get(f"{selected_currency}_TO_EUR", 1.0)
                st.caption(f"1 {selected_currency} = {rate:.4f} EUR")
        
        # Select paths based on view
        years = simulation_years
        
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
        else:
            paths_to_plot = display_results['pension_wealth']
            if show_real:
                cumulative_inflation = np.cumprod(1 + results['inflation_rates'], axis=1)
                cumulative_inflation = np.column_stack([np.ones(n_simulations), cumulative_inflation])
                paths_to_plot = paths_to_plot / cumulative_inflation
            y_label = "Pension Wealth"
        
        # Calculate percentiles
        percentiles = [10, 25, 50, 75, 90]
        percentile_data = np.percentile(paths_to_plot, percentiles, axis=0)
        
        # Create main chart
        fig = go.Figure()
        
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
        
        fig.add_trace(go.Scatter(
            x=list(range(years + 1)),
            y=percentile_data[2],
            mode='lines',
            line=dict(color='darkgreen', width=3),
            name='Median (50th percentile)'
        ))
        
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
        
        fig.update_layout(
            title=f"{y_label} Trajectory: Age {starting_age} to {retirement_age} ({simulation_years} years)",
            xaxis_title="Years from Now",
            yaxis_title=f"{y_label} ({currency_symbol})",
            hovermode='x unified',
            height=600,
            showlegend=True
        )
        
        fig.update_yaxes(tickprefix=currency_symbol, tickformat=",.0f")
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Key metrics
        st.subheader("Key Statistics")
        
        net_worth_paths = display_results['net_worth']  # Always use display currency
        # Convert results to display currency

        # NOW USE display_results INSTEAD OF results
        final_net_worth = display_results['net_worth'][:, -1]
        initial_net_worth = display_results['net_worth'][:, 0]

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            median_final = np.median(final_net_worth)
            st.metric("Median Final Net Worth", format_currency(median_final, selected_currency))
            if show_conversion and selected_currency != 'EUR':
                st.caption(f"≈ €{convert_currency(median_final, selected_currency, 'EUR'):,.0f}")
        
        with col2:
            mean_final = np.mean(final_net_worth)
            st.metric("Mean Final Net Worth", format_currency(mean_final, selected_currency))
            if show_conversion and selected_currency != 'EUR':
                st.caption(f"≈ €{convert_currency(mean_final, selected_currency, 'EUR'):,.0f}")
        
        with col3:
            prob_growth = (final_net_worth > initial_net_worth).mean() * 100
            st.metric("Probability of Growth", f"{prob_growth:.1f}%")
        
        with col4:
            prob_double = (final_net_worth > initial_net_worth * 2).mean() * 100
            st.metric("Probability of 2x Growth", f"{prob_double:.1f}%")
        
        # Wealth composition
        st.subheader("Wealth Composition Over Time (Median Scenario)")
        
        fig_composition = go.Figure()
        
        median_liquid = np.median(display_results['liquid_wealth'], axis=0)
        median_pension = np.median(display_results['pension_wealth'], axis=0)
        median_property = np.median(display_results['property_value'], axis=0)
        median_mortgage = np.median(display_results['mortgage_balance'], axis=0)
        median_equity = median_property - median_mortgage
        median_net_worth = median_liquid + median_pension + median_equity
        
        if show_real:
            inflation_adjustment = np.concatenate([
                [1], 
                np.cumprod(1 + np.median(results['inflation_rates'], axis=0))
            ])
            median_liquid = median_liquid / inflation_adjustment
            median_pension = median_pension / inflation_adjustment
            median_equity = median_equity / inflation_adjustment
            median_net_worth = median_net_worth / inflation_adjustment
        
        fig_composition.add_trace(go.Scatter(
            x=list(range(years + 1)),
            y=median_liquid,
            mode='lines',
            name='Liquid Wealth',
            line=dict(color='#1f77b4', width=2),
            fill='tozeroy',
            fillcolor='rgba(31, 119, 180, 0.3)'
        ))
        
        fig_composition.add_trace(go.Scatter(
            x=list(range(years + 1)),
            y=median_pension,
            mode='lines',
            name='Pension',
            line=dict(color='#ff7f0e', width=2)
        ))
        
        fig_composition.add_trace(go.Scatter(
            x=list(range(years + 1)),
            y=median_equity,
            mode='lines',
            name='Property Equity',
            line=dict(color='#2ca02c', width=2)
        ))
        
        fig_composition.add_trace(go.Scatter(
            x=list(range(years + 1)),
            y=median_net_worth,
            mode='lines',
            name='Total Net Worth',
            line=dict(color='black', width=3, dash='dash')
        ))
        
        fig_composition.add_hline(y=0, line_dash="dot", line_color="gray", opacity=0.5)
        
        fig_composition.update_layout(
            title=f"Wealth Composition: Age {starting_age} to {retirement_age}",
            xaxis_title="Years from Now",
            yaxis_title=f"Value ({currency_symbol})",
            hovermode='x unified',
            height=400,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        fig_composition.update_yaxes(tickprefix=currency_symbol, tickformat=",.0f")
        
        st.plotly_chart(fig_composition, use_container_width=True)
        
        # Export buttons
        st.markdown("---")
        st.subheader("📥 Export Results")
        col_exp1, col_exp2, col_exp3 = st.columns([1, 1, 3])
        
        with col_exp1:
            export_base_events = st.session_state.get('base_events', [])

            excel_file = export_to_excel(
                results,  # Still in base currency (EUR)
                currency_symbol,
                selected_currency,
                base_events,  # Events in base currency
                st.session_state.base_annual_income,  # Base values
                st.session_state.base_monthly_expenses,
                st.session_state.base_liquid_wealth,
                st.session_state.base_property_value,
                st.session_state.base_mortgage
            )
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            st.download_button(
                label="📊 Export to Excel",
                data=excel_file,
                file_name=f"wealth_simulation_{timestamp}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
            
            if st.session_state.get('authenticated', False):
                increment_export_count(st.session_state.user_id)

        with col_exp2:
            if PDF_EXPORT_AVAILABLE:
                pdf_file = export_to_pdf(
                    results,  # Still in base currency (EUR)
                    currency_symbol,
                    selected_currency,
                    base_events,  # Events in base currency
                    fig,
                    fig_composition,
                    st.session_state.base_annual_income,  # Base values
                    st.session_state.base_monthly_expenses,
                    st.session_state.base_liquid_wealth,
                    st.session_state.base_property_value,
                    st.session_state.base_mortgage
                )
                
                st.download_button(
                    label="📄 Export to PDF",
                    data=pdf_file,
                    file_name=f"wealth_simulation_{timestamp}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                
                if st.session_state.get('authenticated', False):
                    increment_export_count(st.session_state.user_id)
            else:
                st.button(
                    label="📄 Export to PDF",
                    disabled=True,
                    use_container_width=True,
                    help="PDF export requires Chrome"
                )
                st.caption("⚠️ PDF unavailable - use Excel export")

        # Annual Cash Flow Summary - Combined Section
        st.markdown("---")
        st.subheader("Annual Cash Flow Summary")
        
        # Calculate Year 1 cash flow
        pension_contrib = gross_annual_income * pension_contribution_rate
        tax = gross_annual_income * effective_tax_rate
        take_home = gross_annual_income - pension_contrib - tax
        annual_expenses_calc = monthly_expenses * 12
        annual_mortgage_calc = calculated_payment * 12
        annual_available_yr1 = take_home - annual_expenses_calc - annual_mortgage_calc
        
        # Check for property events that will change mortgage payments
        future_mortgage_changes = []
        for event in events:
            if event.get('type') == 'property_purchase':
                future_mortgage_changes.append({
                    'year': event['year'],
                    'new_payment': event['new_mortgage_payment'],
                    'description': event['name']
                })
            elif event.get('type') == 'property_sale':
                future_mortgage_changes.append({
                    'year': event['year'],
                    'new_payment': 0,
                    'description': event['name']
                })
        
        # Row 1: Year 1 breakdown and metrics
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Year 1 Cash Flow Breakdown**")
            year1_income = gross_annual_income
            year1_pension = year1_income * pension_contribution_rate
            year1_tax = year1_income * effective_tax_rate
            year1_takehome = year1_income - year1_pension - year1_tax
            year1_expenses = monthly_expenses * 12
            year1_mortgage = st.session_state.get('monthly_mortgage_payment', 0) * 12
            year1_available = year1_takehome - year1_expenses - year1_mortgage
            
            cashflow_df = pd.DataFrame({
                'Item': ['Gross Income', '- Pension Contrib', '- Tax', '= Take Home', 
                        '- Living Expenses', '- Mortgage', '= Available for Investment'],
                'Amount': [
                    format_currency(year1_income, selected_currency),
                    format_currency(year1_pension, selected_currency),
                    format_currency(year1_tax, selected_currency),
                    format_currency(year1_takehome, selected_currency),
                    format_currency(year1_expenses, selected_currency),
                    format_currency(year1_mortgage, selected_currency),
                    format_currency(year1_available, selected_currency)
                ]
            })
            st.dataframe(cashflow_df, use_container_width=True, hide_index=True)
            
            if year1_available < 0:
                st.error(f"⚠️ Cash flow deficit: {format_currency(abs(year1_available), selected_currency)}/year")
            else:
                st.success(f"✓ Annual savings: {format_currency(year1_available, selected_currency)} ({format_currency(year1_available/12, selected_currency)}/month)")
        
        with col2:
            st.markdown("**Key Metrics**")
            st.metric(
                "Year 1 Net Income",
                format_currency(take_home, selected_currency),
                help="Gross income minus taxes and pension contributions"
            )
            st.metric(
                "Year 1 Total Expenses",
                format_currency(annual_expenses_calc + annual_mortgage_calc, selected_currency),
                help="Living expenses plus mortgage payments"
            )
            st.metric(
                "Year 1 Available Savings",
                format_currency(annual_available_yr1, selected_currency),
                delta=f"{(annual_available_yr1/take_home*100):.1f}% of take-home" if take_home > 0 else None,
                help="Amount available to save/invest after all expenses"
            )
            
            if future_mortgage_changes:
                st.info(f"📅 {len(future_mortgage_changes)} property event(s) will change mortgage payments")
        
        # Row 2: Liquid wealth check
        st.markdown("**Liquid Wealth Status**")
        col1, col2, col3 = st.columns(3)
        
        min_liquid = np.median(results['liquid_wealth'], axis=0).min()
        if show_real:
            inflation_adj = np.concatenate([[1], np.cumprod(1 + np.median(results['inflation_rates'], axis=0))])
            min_liquid = (np.median(results['liquid_wealth'], axis=0) / inflation_adj).min()
        
        final_liquid = np.median(results['liquid_wealth'], axis=0)[-1]
        if show_real:
            final_liquid = final_liquid / inflation_adj[-1]
        
        with col1:
            if min_liquid < 0:
                st.error(f"⚠️ Liquid wealth goes negative!")
                st.metric("Minimum Liquid Wealth", format_currency(min_liquid, selected_currency))
            else:
                st.success(f"✓ Liquid wealth stays positive")
                st.metric("Minimum Liquid Wealth", format_currency(min_liquid, selected_currency))
        
        with col2:
            st.metric("Median Final Liquid Wealth", format_currency(final_liquid, selected_currency))
        
        with col3:
            if min_liquid < 0:
                st.markdown("**Recommendations:**")
                st.markdown("- Reduce monthly expenses")
                st.markdown("- Increase income")
                st.markdown("- Review major events")
        
        # Cash Flow Projection with Financial Events
        st.markdown("---")
        st.subheader("Cash Flow Projection with Financial Events")
        
        # Build year-by-year cash flow projection
        # First 10 years: every year, then 5-year intervals
        max_projection_year = min(simulation_years, 30)
        projection_years = list(range(0, min(11, max_projection_year + 1)))
        if max_projection_year > 10:
            projection_years += [y for y in [15, 20, 25, 30] if y <= max_projection_year]
        
        cashflow_projection = []
        
        for year in projection_years:
            # Apply all events up to this year
            year_monthly_expenses = monthly_expenses
            year_monthly_mortgage = calculated_payment
            year_monthly_rental = 0
            event_notes = []
            
            # Convert events from base to display currency for this calculation
            display_events = convert_events_from_base(base_events, selected_currency)
            
            for event in display_events:
                if event['year'] <= year:
                    if event['type'] == 'property_purchase':
                        year_monthly_mortgage = event['new_mortgage_payment']
                        if event['year'] == year:
                            event_notes.append(f"🏠 {event['name']}")
                    elif event['type'] == 'property_sale':
                        year_monthly_mortgage = 0
                        if event['year'] == year:
                            event_notes.append(f"💰 {event['name']}")
                    elif event['type'] == 'expense_change':
                        year_monthly_expenses += event['monthly_change']
                        if event['year'] == year:
                            event_notes.append(f"📊 {event['name']}")
                    elif event['type'] == 'rental_income':
                        year_monthly_rental += event['monthly_rental']
                        if event['year'] == year:
                            event_notes.append(f"🏘️ {event['name']}")
                    elif event['type'] == 'one_time_expense' and event['year'] == year:
                        event_notes.append(f"💸 {event['name']}")
                    elif event['type'] == 'windfall' and event['year'] == year:
                        event_notes.append(f"💵 {event['name']}")
            
            # Calculate cash flow (with salary inflation)
            cumulative_salary_growth = (1 + salary_inflation) ** year
            year_income = gross_annual_income * cumulative_salary_growth
            year_pension = year_income * pension_contribution_rate
            year_tax = year_income * effective_tax_rate
            year_takehome = year_income - year_pension - year_tax
            year_rental_annual = year_monthly_rental * 12
            year_expenses_annual = year_monthly_expenses * 12
            year_mortgage_annual = year_monthly_mortgage * 12
            year_available = year_takehome + year_rental_annual - year_expenses_annual - year_mortgage_annual
            
            cashflow_projection.append({
                'Year': year,
                'Age': starting_age + year,
                'Take Home': format_currency(year_takehome, selected_currency),
                'Rental Income': format_currency(year_rental_annual, selected_currency) if year_rental_annual > 0 else "-",
                'Living Expenses': format_currency(year_expenses_annual, selected_currency),
                'Mortgage': format_currency(year_mortgage_annual, selected_currency) if year_mortgage_annual > 0 else "-",
                'Available Savings': format_currency(year_available, selected_currency),
                'Monthly Savings': format_currency(year_available/12, selected_currency),
                'Events This Year': ', '.join(event_notes) if event_notes else '-'
            })
        
        projection_df = pd.DataFrame(cashflow_projection)
        
        # Style the dataframe to highlight negative values
        def highlight_negative(val):
            if isinstance(val, str) and val.startswith('-') and not val.startswith('--'):
                try:
                    # Check if it's a negative currency value
                    if any(symbol in val for symbol in ['€', '$', '£', 'C$', 'A$', 'NZ$', 'S$', 'HK$', 'CHF', 'kr', '¥', '₹']):
                        return 'background-color: #ffcccc'
                except:
                    pass
            return ''
        
        st.dataframe(
            projection_df.style.applymap(highlight_negative, subset=['Available Savings', 'Monthly Savings']),
            use_container_width=True,
            hide_index=True
        )
        
        st.caption("💡 Take-home income grows with salary inflation. Expenses and mortgage shown in nominal dollars (not inflation-adjusted).")
        st.caption("📝 Events: 🏠 Property Purchase, 💰 Property Sale, 📊 Expense Change, 🏘️ Rental Income, 💸 One-Time Expense, 💵 Windfall")
        
        # Net Worth by Age Milestones
        st.markdown("---")
        st.subheader("Net Worth by Age Milestones")
        
        milestone_years = [5, 10, 15, 20, 25, 30]
        milestone_data = []
        
        for year in milestone_years:
            if year <= simulation_years:
                age_at_milestone = starting_age + year
                year_wealth = display_results['net_worth'][:, year]
                
                milestone_data.append({
                    'Year': year,
                    'Age': age_at_milestone,
                    '10th': format_currency(np.percentile(year_wealth, 10), selected_currency),
                    '25th': format_currency(np.percentile(year_wealth, 25), selected_currency),
                    '50th': format_currency(np.percentile(year_wealth, 50), selected_currency),
                    '75th': format_currency(np.percentile(year_wealth, 75), selected_currency),
                    '90th': format_currency(np.percentile(year_wealth, 90), selected_currency),
                })
        
        milestone_df = pd.DataFrame(milestone_data)
        st.dataframe(milestone_df, use_container_width=True, hide_index=True)
        
        # Distribution at key years
        st.markdown("---")
        st.subheader("Wealth Distribution at Key Milestones")
        
        milestone_years_dist = [y for y in [5, 10, 15, 20, 25, 30] if y <= simulation_years]
        
        if len(milestone_years_dist) >= 3:
            n_rows = 2
            n_cols = 3
        elif len(milestone_years_dist) >= 2:
            n_rows = 1
            n_cols = len(milestone_years_dist)
        else:
            n_rows = 1
            n_cols = 1
        
        fig_dist = make_subplots(
            rows=n_rows, cols=n_cols,
            subplot_titles=[f"Year {y} (Age {starting_age + y})" for y in milestone_years_dist[:n_rows*n_cols]]
        )
        
        for idx, year in enumerate(milestone_years_dist[:n_rows*n_cols]):
            row = idx // n_cols + 1
            col = idx % n_cols + 1
            
            if year < paths_to_plot.shape[1]:
                fig_dist.add_trace(
                    go.Histogram(
                        x=paths_to_plot[:, year],
                        nbinsx=50,
                        name=f"Year {year}",
                        showlegend=False,
                        marker_color='rgba(31, 119, 180, 0.7)'
                    ),
                    row=row, col=col
                )
        
        fig_dist.update_layout(height=400 if n_rows == 1 else 600, showlegend=False)
        fig_dist.update_xaxes(tickprefix=currency_symbol, tickformat=",.0f")
        fig_dist.update_yaxes(title_text="Frequency")
        
        st.plotly_chart(fig_dist, use_container_width=True)


    else:
        st.info("👈 Set your parameters in the sidebar and click 'Run Simulation' to begin")
        st.markdown("""
        ### How to Use This Tool
        
        1. **Select Currency**: Choose your preferred currency - values will convert automatically when you switch
        2. **Set Initial Position**: Enter your current liquid wealth, property value, and mortgage balance
        3. **Configure Income & Tax**: Set gross income, tax rate, and pension contribution rate
        4. **Monthly Budget**: Enter living expenses
        5. **Run Simulation**: Click the button to generate Monte Carlo paths
        
        **Currency Conversion:** When you change currencies, all your entered values will automatically convert using current exchange rates.
        """)