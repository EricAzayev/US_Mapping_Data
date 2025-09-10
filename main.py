import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px


def normalize_color_theme(theme: str):
    return theme.capitalize(), theme.lower()

def make_heatmap(input_df, input_y, input_x, input_color, input_color_theme):
    heatmap = alt.Chart(input_df).mark_rect().encode(
        y=alt.Y(f'{input_y}:O', axis=alt.Axis(
            title="Year", titleFontSize=18, titlePadding=15,
            titleFontWeight=900, labelAngle=0)),
        x=alt.X(f'{input_x}:O', axis=alt.Axis(
            title="State", titleFontSize=18, titlePadding=15,
            titleFontWeight=900)),
        color=alt.Color(f'{input_color}:Q',
                        legend=None,
                        scale=alt.Scale(scheme=input_color_theme.lower())),
        stroke=alt.value('black'),
        strokeWidth=alt.value(0.25),
    ).properties(width=900
    ).configure_axis(
        labelFontSize=12,
        titleFontSize=12
    )
    return heatmap


def make_choropleth(input_df, input_id, input_column, input_color_theme):
   
    choropleth = px.choropleth(
        input_df,
        locations="Code",  
        locationmode="USA-states",
        color=input_column,
        color_continuous_scale=input_color_theme.lower(),
        scope="usa",
        labels={input_column: 'Poverty Rate (%)'}
    )
    choropleth.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(l=0, r=0, t=0, b=0),
        height=350
    )
    return choropleth


df = pd.read_csv('state_poverty_rates.csv')

state_abbrev = {
    "Alabama":"AL","Alaska":"AK","Arizona":"AZ","Arkansas":"AR","California":"CA","Colorado":"CO","Connecticut":"CT",
    "Delaware":"DE","Florida":"FL","Georgia":"GA","Hawaii":"HI","Idaho":"ID","Illinois":"IL","Indiana":"IN",
    "Iowa":"IA","Kansas":"KS","Kentucky":"KY","Louisiana":"LA","Maine":"ME","Maryland":"MD","Massachusetts":"MA",
    "Michigan":"MI","Minnesota":"MN","Mississippi":"MS","Missouri":"MO","Montana":"MT","Nebraska":"NE","Nevada":"NV",
    "New Hampshire":"NH","New Jersey":"NJ","New Mexico":"NM","New York":"NY","North Carolina":"NC","North Dakota":"ND",
    "Ohio":"OH","Oklahoma":"OK","Oregon":"OR","Pennsylvania":"PA","Rhode Island":"RI","South Carolina":"SC",
    "South Dakota":"SD","Tennessee":"TN","Texas":"TX","Utah":"UT","Vermont":"VT","Virginia":"VA","Washington":"WA",
    "West Virginia":"WV","Wisconsin":"WI","Wyoming":"WY"
}
df["Code"] = df["State"].map(state_abbrev)


df_reshaped = df.melt(id_vars=["State"], var_name="Year", value_name="Poverty Rate")

st.set_page_config(
    page_title="State Poverty Rates Dashboard",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded",
)
alt.themes.enable("dark")

with st.sidebar:
    st.title("State Poverty Rates")
    st.markdown("## Select State")

    year_list = ['2003', '2013', '2023']
    selected_year = st.selectbox('Select a year', year_list, index=2)
    color_theme_list = ['blues', 'cividis', 'greens', 'inferno', 'magma',
                        'plasma', 'reds', 'rainbow', 'turbo', 'viridis']
    selected_color_theme = st.selectbox('Select a color theme', color_theme_list)

df_selected_year = df[["State", "Code", selected_year]].rename(columns={selected_year: "Poverty Rate"})
df_selected_year_sorted = df_selected_year.sort_values("Poverty Rate", ascending=False)

col = st.columns((1.5, 4.5, 2), gap='medium')

col = st.columns((1.5, 4.5, 2), gap='medium')

with col[1]:
    st.markdown('#### State Poverty Rate Choropleth')
    choropleth = make_choropleth(df_selected_year, 'Code', 'Poverty Rate', selected_color_theme)
    st.plotly_chart(choropleth, use_container_width=True)

with col[2]:
    st.markdown('#### Top States by Poverty Rate')
    st.dataframe(
        df_selected_year_sorted[["State", "Poverty Rate"]],
        hide_index=True,
        column_config={
            "State": st.column_config.TextColumn("State"),
            "Poverty Rate": st.column_config.ProgressColumn(
                "Poverty Rate (%)",
                format="%.1f",
                min_value=0,
                max_value=30,
            )
        }
    )
    with st.expander('About', expanded=True):
        st.write('''
            - Data: [U.S. Census Bureau](https://www.census.gov/data/datasets/time-series/demo/popest/2010s-state-total.html).
            - This dashboard visualizes state-level poverty rates for 2003, 2013, and 2023.
        ''')

st.markdown("### Poverty Rate by Year (Heatmap)")
heatmap = make_heatmap(df_reshaped, 'Year', 'State', 'Poverty Rate', selected_color_theme)
st.altair_chart(heatmap, use_container_width=True)
