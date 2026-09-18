from cashdash.accumulator import Accumulator
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import pandas as pd
import streamlit as st


# Page config settings
st.set_page_config(page_title="Portfolio")


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$    FUNCTION DEFINITIONS       $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

# Cache the instanced accumulator class such that it does not rerun during app update
@st.cache_resource
def create_instance() -> Accumulator:
    instance = Accumulator()
    instance.load_assets()
    
    return instance

def create_growth_figure(df: pd.DataFrame) -> Figure:
    # Plot figure
    fig, ax = plt.subplots()
    ax.plot(df["Current worth"])
    ax.set_xlabel("Date")
    ax.set_ylabel("Portfolio worth (€)")
    ax.set_title("Asset growth over time")
    
    return fig


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$    APP LAYOUT SKELETON       $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

st.header("Portfolio Growth")
net_worth_area = st.container()

toggle_debt = st.checkbox("Include debt", value=True)

chart_area = st.container()



# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$    APP LOGIC       $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

# Create accumulator instance on startup. Is cached afterwards
accumulator = create_instance()

# Update with current toggle settings and recalculate aggregated data
accumulator.update("t_debt_duo.csv", toggle_debt)
df = accumulator.calc_agg_data()

# Fill containers with aggregated data
with net_worth_area:
    st.metric("Current worth", f"€{df['Current worth'].iloc[-1]:.0f}")
with chart_area:
    st.pyplot(create_growth_figure(df))
    st.dataframe(df.tail(10), width='stretch')
