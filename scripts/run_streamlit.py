from cashdash.accumulator import Accumulator
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter
import pandas as pd
import numpy as np
import streamlit as st


# Page config settings
st.set_page_config(page_title="Portfolio")
plt.style.use('dark_background')

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$    FUNCTION DEFINITIONS       $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

# Cache the instanced accumulator class such that it does not rerun during app update
@st.cache_resource
def create_instance() -> Accumulator:
    instance = Accumulator()
    instance.load_assets()
    
    return instance

# Create asset growth figure
def create_growth_figure(df: pd.DataFrame) -> Figure:
    # Plot figure
    fig, ax = plt.subplots(facecolor='#0E1117')
    ax.set_facecolor('#0E1117')
    
    # Plot graph and fill
    ax.plot(df["Current worth"], lw=2, color='g', alpha=0.8)
    ax.fill_between(df.index, df["Current worth"], 0, color='g', alpha=0.5)
    
    # Set y limit to 0, or below lowest value when negative
    ax.set_ylim(bottom=min(1.1*df["Current worth"].min(), 0))
    
    # Title
    ax.set_title("Portfolio worth (€)")
    ax.title.set_fontweight('bold')
    
    # Change y-axis format from 10000.21, to €10k and hide ticks
    ax.get_yaxis().set_major_formatter(FuncFormatter(
        lambda x, _: "€ " + str(int(x/1000)) + "k"
    ))
    ax.tick_params(axis=u'both', which=u'both',length=0)
    
    # Remove frame border lines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

    return fig


def create_nested_allocation_pie(df_dict: dict[str, pd.DataFrame], metadata: pd.DataFrame, asset_sel: list[bool]) -> Figure:
    
    # Determines pie radius size of both pie's
    size = 0.3

    # Obtain latest worth for each included stocks and savings asset type
    df = metadata.copy().sort_values(["ASSET_TYPE", "COMPANY"])
    df["Current worth"] = 0.
    for idx, row in df.iterrows():
        df.loc[idx, "Current worth"] = df_dict[row["FILENAME"]]["Current worth"].iloc[-2] #TODO: readjust to -1

    # Obtain current worth of all included assets per type and per company
    asset_sel = [x for x in asset_sel if x != "Debt"]
    asset_vals = df[(df["ASSET_TYPE"].isin(asset_sel)) & (df["TO_INCLUDE"])].groupby("ASSET_TYPE")["Current worth"].sum()
    company_vals = df[(df["ASSET_TYPE"].isin(asset_sel)) & (df["TO_INCLUDE"])].groupby(["ASSET_TYPE", "COMPANY"])["Current worth"].sum()
        
    # Create figure and colors
    fig, ax = plt.subplots(facecolor='#0E1117')
    tab20c = plt.color_sequences["tab20c"]
    outer_colors_indices = [x*4 for x in range(len(asset_vals.index.unique()))]
    inner_colors_indices = [[n*4 + x+1 for x in range(len(company_vals.loc[asset_sel[n]].index))] 
                                for n in range(len(asset_vals.index.unique()))]
    outer_colors = [tab20c[i] for i in outer_colors_indices]
    inner_colors = [tab20c[i] for i in np.concatenate(inner_colors_indices).tolist()]
    
    # Plot pie charts
    ax.pie(asset_vals, radius=1, colors=outer_colors, autopct='%1.0f%%', pctdistance=1-(size/2),
            textprops={"weight": "bold"}, wedgeprops=dict(width=size, edgecolor='w'), labels=asset_vals.index)
    
    wedges, labels = ax.pie(company_vals, radius=1-size, labeldistance=1-(size), colors=inner_colors, 
            textprops={"size": 8, "weight": "bold", "color": "black"},
            wedgeprops=dict(width=size, edgecolor='w'), labels=company_vals.index.get_level_values(1))
    
    # Rotate inner labels to be diagonal to angle
    for ea, eb in zip(wedges, labels):
        mang =(ea.theta1 + ea.theta2)/2.  # get mean_angle of the wedge
        eb.set_rotation(mang+270)         # rotate the label by (mean_angle + 270)
        eb.set_va("center")
        eb.set_ha("center")
    
    ax.set(aspect="equal", title='Pie plot with `ax.pie`')
    return fig   


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$    APP LAYOUT SKELETON       $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

st.header("Portfolio Growth")
net_worth_area = st.container()

# Button area
owner_multiselect_area = st.container()
asset_toggles_area = st.container()

# Charts 
chart_area = st.container()



# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$    APP LOGIC       $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

# Create accumulator instance on startup. Is cached afterwards
accumulator = create_instance()
meta = accumulator.metadata

with owner_multiselect_area:
    st.sidebar.header("Options")
    owners_sel = st.sidebar.multiselect(
        "Owners",
        options=sorted(meta["OWNER"].unique()),
        default=sorted(meta["OWNER"].unique()),
    )
with asset_toggles_area:
    asset_type_sel = [
        asset_type for asset_type in sorted(meta["ASSET_TYPE"].unique())
        if st.sidebar.checkbox(asset_type, value=(asset_type != "Debt"), key=f"ac_{asset_type}")
    ]

# Update with current toggle settings and recalculate aggregated data
try:
    accumulator.select(OWNER=owners_sel, ASSET_TYPE=asset_type_sel)
except ValueError:
    st.warning("Currently no financial data is selected. Select at least 1 owner and 1 asset type to view the information. ")

# 
df = accumulator.calc_agg_data()

# Fill containers with aggregated data
with net_worth_area:
    st.metric("Current worth", f"€{df['Current worth'].iloc[-1]:.2f}")

with chart_area:
    st.pyplot(create_growth_figure(df))
    st.pyplot(create_nested_allocation_pie(accumulator.data_dict, meta, asset_type_sel))
    #st.dataframe(df.tail(10), width='stretch')
