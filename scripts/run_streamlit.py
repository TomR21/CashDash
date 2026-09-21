from cashdash.accumulator import Accumulator
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter
import pandas as pd
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
    #st.dataframe(df.tail(10), width='stretch')
