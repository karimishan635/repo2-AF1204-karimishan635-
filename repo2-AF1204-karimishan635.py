# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo>=0.19.10",
#     "pandas>=2.3.3",
#     "plotly>=6.5.1",
#     "pyarrow>=22.0.0",
#     "pyzmq>=27.1.0",
# ]
# ///

import marimo

__generated_with = "0.19.11"
app = marimo.App()


@app.cell
def _(mo):
    mo.md(r"""
    ---
    ## 🎓 Interactive Finance Portfolio
    This multi-tabbed portfolio showcases my skills in financial data analysis, interactive visualisation, 
    and Python-based applications using real-world company data.
    """)
    return


@app.cell
def _():

    import marimo as mo
    import pandas as pd

    # Require micropip to install packages in the WASM environment
    import micropip

    return micropip, mo, pd


@app.cell
def _(pd):
    # 1: Setup & Data Prep

    # Get data ready for the dynamic webpage

    # Note: The local-data-loading approach below does not work due to GitHub Pages compression issue
    #===============================================================================================
    # Must place data file in subfolder 'public' of the folder where the marimo notebook is located
    # (required to locate and include the data when exporting as html-wasm)
    #
    #filename = mo.notebook_location() / "public" / 'sp500_ZScore_AvgCostofDebt.csv'
    #df_final = pd.read_csv(str(filename))

    # Instead, use a raw gist URL approach to remotely load the data (already hosted online)
    #=======================================================================================
    csv_url = "https://gist.githubusercontent.com/DrAYim/80393243abdbb4bfe3b45fef58e8d3c8/raw/ed5cfd9f210bf80cb59a5f420bf8f2b88a9c2dcd/sp500_ZScore_AvgCostofDebt.csv"

    df_final = pd.read_csv(csv_url)  # as opposed to pd.read_csv('public/sp500_ZScore_AvgCostofDebt.csv')

    df_final = df_final.dropna(subset=['AvgCost_of_Debt', 'Z_Score_lag', 'Sector_Key'])
    # Filter outliers to reduce distortion in visualizations
    df_final = df_final[(df_final['AvgCost_of_Debt'] < 5)]   # 5 means 500%
    #df_final = df_final[(df_final['AvgCost_of_Debt'] > 0) & (df_final['Z_Score_lag'] < 20)]
    df_final['Debt_Cost_Percent'] = df_final['AvgCost_of_Debt'] * 100
    return (df_final,)


@app.cell
def _(df_final, mo):
    # 2: Define the UI Controls (The "Inputs")

    # create the widgets here. In marimo, assigning them to a variable makes them available globally.

    # 1. A Dropdown to select Sectors
    all_sectors = sorted(df_final['Sector_Key'].unique().tolist())
    sector_dropdown = mo.ui.multiselect(
        options=all_sectors,
        value=all_sectors[:3], # Default to first 3
        label="Filter by Sector",
        )

    # 2. A Slider for Market Cap (Size of company)
    # Convert Market Cap to Billions for easier reading
    df_final['Market_Cap_B'] = df_final['Market_Cap'] / 1e9
    max_cap = int(df_final['Market_Cap_B'].max())

    cap_slider = mo.ui.slider(
        start=0,
        stop=200,   # int(0.05*max_cap),
        step=10,
        value=0, # initial value
        label="Min Market Cap ($ Billions)"
        )
    return cap_slider, sector_dropdown


@app.cell
def _(cap_slider, df_final, sector_dropdown):
    # 3: The Filter Logic (Reactive Data)

    # This cell re-runs automatically when the user changes the slider or dropdown

    # Filter the dataframe based on the UI inputs
    filtered_portfolio = df_final[
        (df_final['Sector_Key'].isin(sector_dropdown.value)) &
        (df_final['Market_Cap_B'] >= cap_slider.value)
        ]

    # Calculate a quick summary metric
    count = len(filtered_portfolio)
    return count, filtered_portfolio


@app.cell
async def _(micropip):
    # Await installation of plotly in the WASM environment
    await micropip.install('plotly');

    import plotly.express as px

    return (px,)


@app.cell
def _(count, filtered_portfolio, mo, pd, px):
    # 4: The Visualizations

    #=========================================
    # Plot 1: The Financial Analysis (Scatter)
    #=========================================
    fig_portfolio = px.scatter(
        filtered_portfolio,
        x='Z_Score_lag',
        y='Debt_Cost_Percent',
        color='Sector_Key',
        size='Market_Cap_B',
        hover_name='Name',
        title=f"Cost of Debt vs. Z-Score ({count} observations)",
        labels={'Z_Score_lag': 'Altman Z-Score (lagged)', 'Debt_Cost_Percent': 'Avg. Cost of Debt (%)'},
        template='presentation',
        width=900,
        height=600
        )

    # Add a vertical line for the "Distress" threshold (1.81)
    fig_portfolio.add_vline(x=1.81, line_dash="dash", line_color="red",
        annotation=dict(
            text="Distress Threshold (Z-Score = 1.81)",
            font=dict(color="red"),
            x=1.5, xref="x",
            y=1.07, yref="paper",
            showarrow=False,
            yanchor="top"
            )
        )

    # Add a vertical line for the "Safe" threshold (2.99)
    fig_portfolio.add_vline(x=2.99, line_dash="dash", line_color="green",
        annotation=dict(
            text="Safe Threshold (Z-Score = 2.99)",
            font=dict(color="green"),
            x=3.10, xref="x",
            y=1.02, yref="paper",
            showarrow=False,
            yanchor="top"
            )
        )

    chart_element = mo.ui.plotly(fig_portfolio)

    #=========================================
    # Plot 2: Personal Travel Map
    #=========================================
    travel_data = pd.DataFrame({
        'City': ['London', 'New York', 'Tokyo', 'Sydney', 'Paris'],
        'Lat': [51.5, 40.7, 35.6, -33.8, 48.8],
        'Lon': [-0.1, -74.0, 139.6, 151.2, 2.3],
        'Visit_Year_str': ['2022', '2023', '2024', '2021', '2023']
    })

    years = sorted(travel_data['Visit_Year_str'].unique(), key=int)

    fig_travel = px.scatter_geo(
        travel_data,
        lat='Lat', lon='Lon',
        hover_name='City',
        color='Visit_Year_str',
        category_orders={'Visit_Year_str': years},
        color_discrete_sequence=px.colors.qualitative.Plotly,
        projection="natural earth",
        title="My Travel Footprint",
        labels={'Visit_Year_str': 'Visit Year'}
    )

    fig_travel.update_traces(marker=dict(size=12));
    return chart_element, fig_travel


@app.cell
def _(cap_slider, chart_element, fig_travel, mo, sector_dropdown):
    # 5: The "Portfolio" Layout (a Multi-Tab Webpage)

    tab_cv = mo.md(
        """
        ### Aspiring Finance Professional | Data Analysis Enthusiast

        **About Me:**
        I am Mohammed Abdul Karim Ishan, a first-year BSc Accounting and Finance student with a strong interest 
        in finance, financial analysis, and data-driven decision-making. I enjoy using technology and data tools 
        to explore business problems and present insights in a clear, interactive way.

        **Education:**
        - **BSc Accounting & Finance**, Year 1
        - Relevant areas of study: Financial Accounting, Finance, Data Analysis

        **Technical Skills:**
        - Python
        - Pandas
        - Plotly
        - Excel
        - GitHub
        - Marimo

        **Project Experience:**
        - Built this individual interactive finance portfolio using Marimo and Plotly
        - Collaborated on a group project to create an interactive dashboard analysing S&P 500 company financials
        """
    )

    tab_data_content = mo.vstack([
        mo.md("""
## 📊 Credit Risk vs Cost of Debt Analysis

This interactive dashboard explores the relationship between company credit risk and borrowing costs 
using S&P 500 financial data.

- Credit risk is represented by the Altman Z-Score
- Borrowing cost is represented by the average cost of debt
- Users can filter the analysis by sector and market capitalisation

This project demonstrates my ability to work with financial datasets, apply data filtering, 
and build interactive visualisations using Python.
"""),
        mo.callout(
            mo.md("Use the filters below to explore how credit risk and cost of debt vary across sectors and company sizes."),
            kind="info"
        ),
        mo.hstack([sector_dropdown, cap_slider], justify="center", gap=2),
        chart_element
    ])

    tab_personal = mo.vstack([
        mo.md("""
## 🌍 Personal Interests

Outside of my academic work, I have strong interests in:

- Football
- Cars
- Travel

This section adds a different style of visualisation to my portfolio and reflects my interest 
in presenting information in engaging and interactive ways.
"""),
        mo.ui.plotly(fig_travel)
    ])
    return tab_cv, tab_data_content, tab_personal


@app.cell
def _(mo, tab_cv, tab_data_content, tab_personal):
    # 6: Assemble and display the multi-tab webpage

    app_tabs = mo.ui.tabs({
        "📄 About Me": tab_cv,
        "📊 Financial Data Analysis Project": tab_data_content,
        "✈️ Personal Interests": tab_personal,
        "🧠 Reflection": mo.md("""
## Reflection

Through this project, I developed practical skills in:

- Data cleaning and preparation using Pandas
- Financial data analysis using S&P 500 company information
- Building interactive dashboards with Marimo
- Data visualisation using Plotly
- Managing project progress with GitHub

This project helped me understand how financial information can be transformed into interactive tools 
that support clearer analysis and decision-making.
""")
    })

    mo.md(
        f"""
        # **Mohammed Abdul Karim Ishan**
        ### BSc Accounting & Finance | Year 1

        Welcome to my interactive portfolio. This project demonstrates my ability to analyse financial data, 
        build interactive dashboards, and present insights using Python-based tools.

        ---
        {app_tabs}
        """)
    return


if __name__ == "__main__":
    app.run()
