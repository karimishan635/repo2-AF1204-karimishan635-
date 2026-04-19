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
    import micropip
    return micropip, mo, pd


@app.cell
def _(pd):
    csv_url = "https://gist.githubusercontent.com/DrAYim/80393243abdbb4bfe3b45fef58e8d3c8/raw/ed5cfd9f210bf80cb59a5f420bf8f2b88a9c2dcd/sp500_ZScore_AvgCostofDebt.csv"

    df_final = pd.read_csv(csv_url)
    df_final = df_final.dropna(subset=['AvgCost_of_Debt', 'Z_Score_lag', 'Sector_Key'])
    df_final = df_final[(df_final['AvgCost_of_Debt'] < 5)]
    df_final['Debt_Cost_Percent'] = df_final['AvgCost_of_Debt'] * 100
    df_final['Market_Cap_B'] = df_final['Market_Cap'] / 1e9
    return (df_final,)


@app.cell
def _(df_final, mo):
    all_sectors = sorted(df_final['Sector_Key'].unique().tolist())

    sector_dropdown = mo.ui.multiselect(
        options=all_sectors,
        value=all_sectors,
        label="Filter by Sector",
    )

    max_cap = int(df_final['Market_Cap_B'].max())

    cap_slider = mo.ui.slider(
        start=0,
        stop=max_cap,
        step=max(1, max_cap // 20),
        value=0,
        label="Min Market Cap ($ Billions)"
    )

    return cap_slider, sector_dropdown


@app.cell
def _(cap_slider, df_final, sector_dropdown):
    filtered_portfolio = df_final[
        (df_final['Sector_Key'].isin(sector_dropdown.value)) &
        (df_final['Market_Cap_B'] >= cap_slider.value)
    ]

    count = len(filtered_portfolio)
    return count, filtered_portfolio


@app.cell
async def _(micropip):
    await micropip.install('plotly')
    import plotly.express as px
    return (px,)


@app.cell
def _(count, filtered_portfolio, mo, pd, px):
    if filtered_portfolio.empty:
        chart_element = mo.md("""
### No data available

Try:
- selecting more sectors
- lowering the minimum market cap
""")
    else:
        fig_portfolio = px.scatter(
            filtered_portfolio,
            x='Z_Score_lag',
            y='Debt_Cost_Percent',
            color='Sector_Key',
            size='Market_Cap_B',
            hover_name='Name',
            title=f"Cost of Debt vs. Z-Score ({count} observations)",
            labels={
                'Z_Score_lag': 'Altman Z-Score (lagged)',
                'Debt_Cost_Percent': 'Avg. Cost of Debt (%)'
            },
            template='plotly_white',
            width=900,
            height=600
        )

        fig_portfolio.add_vline(x=1.81, line_dash="dash", line_color="red")
        fig_portfolio.add_vline(x=2.99, line_dash="dash", line_color="green")

        chart_element = mo.ui.plotly(fig_portfolio)

    travel_data = pd.DataFrame({
        'City': ['London', 'New York', 'Tokyo', 'Sydney', 'Paris'],
        'Lat': [51.5, 40.7, 35.6, -33.8, 48.8],
        'Lon': [-0.1, -74.0, 139.6, 151.2, 2.3],
        'Visit_Year_str': ['2022', '2023', '2024', '2021', '2023']
    })

    years = sorted(travel_data['Visit_Year_str'].unique(), key=int)

    fig_travel = px.scatter_geo(
        travel_data,
        lat='Lat',
        lon='Lon',
        hover_name='City',
        color='Visit_Year_str',
        category_orders={'Visit_Year_str': years},
        color_discrete_sequence=px.colors.qualitative.Plotly,
        projection="natural earth",
        title="My Travel Footprint",
        labels={'Visit_Year_str': 'Visit Year'}
    )

    fig_travel.update_traces(marker=dict(size=12))
    return chart_element, fig_travel


@app.cell
def _(cap_slider, chart_element, fig_travel, mo, sector_dropdown):
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
## 📊 Interactive Financial Analysis

This dashboard allows users to explore S&P 500 company financial data using interactive filters.
"""),
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
    app_tabs = mo.ui.tabs({
        "📄 About Me": tab_cv,
        "📊 Interactive Analysis": tab_data_content,
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

        Aspiring finance professional with an interest in financial analysis, data visualisation, and interactive reporting.

        ---
        {app_tabs}
        """
    )
    return


if __name__ == "__main__":
    app.run()
