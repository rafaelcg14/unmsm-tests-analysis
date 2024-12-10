import streamlit as st
import pandas as pd
import os
import altair as alt
import pathlib

from src.utils.handle_data import load_dataframe, career_exists_for_year, generate_analysis

# Set page config
st.set_page_config(
    page_title="Exámenes de Admisión UNMSM - Dashboard",
    page_icon=":school:",
    layout="wide",
    initial_sidebar_state="collapsed")

# Apply CSS
def load_css(file_path):
    with open(file_path) as f:
        st.html(f"<style>{f.read()}</style>")

css_path = pathlib.Path("styles.css")
load_css(css_path)


# Methods
@st.cache_data
def load_dataframe_cached(year, career):
    return load_dataframe(year, career)

@st.cache_data
def genereate_analysis_cached(df, analysis_type, **kwargs):
    return generate_analysis(df, analysis_type, **kwargs)


# Dashboard Layout
st.header("Exámenes de Admisión UNMSM - Dashboard :bar_chart:")

# Filters
years_list = os.listdir('data/processed')

filter_col1, filter_col2 = st.columns(2)

with filter_col1:
    year_option = st.selectbox('Año del examen:', years_list, placeholder='Seleccione el año')

filepath = os.listdir(f'data/processed/{year_option}')
careers_list = [file.split(".csv")[0].split(f"{year_option}-")[1] for file in filepath]

with filter_col2:
    career_option = st.selectbox(
        'Carrera profesional:',
        careers_list,
        placeholder='Seleccione la carrera'
    )

# Load data
try:
    # Load the dataframe for the selected year
    if career_exists_for_year(year_option, career_option):
        df = load_dataframe_cached(year_option, career_option)
    else:
        st.info(f"No se encontró información para la carrera {career_option} en el año {year_option}.")
        df = None

    # Load dataframes for the rest of the years
    valid_years = [year for year in years_list if career_exists_for_year(year, career_option)]
    if valid_years:
        dataframes = {year: load_dataframe_cached(year, career_option) for year in valid_years}
    else:
        st.info(f"No se encontraron datos para la carrera {career_option} en ningún año seleccionado.")
        dataframes = {}

except FileNotFoundError:
    st.info("No se encontró algún archivo.")


# Plots
cols = st.columns(4)

metrics = genereate_analysis_cached(df, analysis_type="kpis", career=career_option)

for i, key, value in zip(range(4), metrics.keys(), metrics.values()):
    with cols[i]:
        with st.container(border=True):
            st.metric(label=key, value=value)
            
cols = st.columns([3, 1])

with cols[0]:
    with st.container(border=True):
        general_analysis_chart = genereate_analysis_cached(df, analysis_type="general", career=career_option)
        st.altair_chart(general_analysis_chart, theme="streamlit", use_container_width=True)

    with st.container(border=True):
        trend_chart = genereate_analysis_cached(df, analysis_type="trend_over_years", career=career_option, dataframes=dataframes)
        st.altair_chart(trend_chart, theme="streamlit", use_container_width=True)
    
with cols[1]:
    with st.container(border=True):
        st.write("##### Top 10 puntajes")
        genereate_analysis_cached(df, analysis_type="top_10_scores", career=career_option)

cols = st.columns(2)

hist1, hist2, bp1, bp2 = genereate_analysis_cached(df, analysis_type="score_range", career=career_option)

with cols[0]:
    with st.container(border=True):
        st.altair_chart(bp1, theme="streamlit", use_container_width=True)
        st.altair_chart(hist1, theme="streamlit", use_container_width=True)

with cols[1]:
    with st.container(border=True):
        st.altair_chart(bp2, theme="streamlit", use_container_width=True)
        st.altair_chart(hist2, theme="streamlit", use_container_width=True)

# Footer
st.markdown(
    """
    ---
    Dashboard creado por [Rafael Castellanos](https://rafaelcg14.github.io/rafael-castellanos-portfolio/)
    """
)