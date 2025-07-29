import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from datetime import datetime # Make sure to import datetime

# --- Page Configuration ---
st.set_page_config(page_title="Options Open Interest Analyzer", layout="wide")
st.title("📈 Options Open Interest Analyzer")

# --- User Inputs in the Sidebar ---
st.sidebar.header("User Inputs")

# --- ADD THIS LINE ---
st.sidebar.caption(f"Data refreshed: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")

# Input box for the ticker symbol
ticker_symbol = st.sidebar.text_input("Enter Stock Ticker:", "PLTR").upper()

if ticker_symbol:
    try:
        # --- Data Fetching ---
        with st.spinner(f"Fetching data for {ticker_symbol}..."):
            stock = yf.Ticker(ticker_symbol)
            
            # Fetch expiration dates - show an error if none are found
            expiration_dates = stock.options
            if not expiration_dates:
                st.error(f"No options data found for ticker '{ticker_symbol}'. Please check the ticker.")
                st.stop()

        # Dropdown for selecting expiration date
        selected_date = st.sidebar.selectbox("Select Expiration Date:", expiration_dates)

        # --- Chart Generation ---
        if selected_date:
            with st.spinner(f"Generating chart for {selected_date}..."):
                option_chain = stock.option_chain(selected_date)
                calls = option_chain.calls
                puts = option_chain.puts

                # Check if there is any open interest to plot
                if calls['openInterest'].sum() == 0 and puts['openInterest'].sum() == 0:
                    st.warning(f"The selected options chain for {selected_date} has no open interest. Please select a different date.")
                else:
                    # Merge data for plotting
                    merged_df = pd.merge(calls[['strike', 'openInterest']], puts[['strike', 'openInterest']], on='strike', suffixes=('_call', '_put'))
                    merged_df.rename(columns={'openInterest_call': 'Call OI', 'openInterest_put': 'Put OI'}, inplace=True)

                    # Create the bar chart
                    fig, ax = plt.subplots(figsize=(18, 9))
                    bar_width = 0.4
                    strikes = merged_df['strike']
                    x_pos = range(len(strikes))

                    ax.bar([i - bar_width/2 for i in x_pos], merged_df['Call OI'], width=bar_width, label='Call OI (Resistance)', color='green')
                    ax.bar([i + bar_width/2 for i in x_pos], merged_df['Put OI'], width=bar_width, label='Put OI (Support)', color='red')

                    # Formatting the chart
                    ax.set_title(f'{ticker_symbol} Options Open Interest for {selected_date}', fontsize=20, pad=20)
                    ax.set_xlabel('Strike Price ($)', fontsize=14)
                    ax.set_ylabel('Number of Contracts (Open Interest)', fontsize=14)
                    ax.legend(fontsize=12)
                    ax.set_xticks(x_pos)
                    ax.set_xticklabels(strikes, rotation=90, ha='center')
                    ax.get_yaxis().set_major_formatter(mticker.FuncFormatter(lambda val, pos: f'{int(val):,}'))
                    ax.grid(axis='y', linestyle='--', alpha=0.7)
                    
                    # Automatically adjust x-axis ticks to prevent clutter
                    if len(strikes) > 50:
                        ax.xaxis.set_major_locator(mticker.MaxNLocator(nbins=50, integer=True))

                    fig.tight_layout()
                    
                    # Display the plot in the Streamlit app
                    st.pyplot(fig)

    except Exception as e:
        st.error(f"An error occurred. The ticker '{ticker_symbol}' may be invalid or there might be an issue fetching data.")
        st.error(f"Error details: {e}")
