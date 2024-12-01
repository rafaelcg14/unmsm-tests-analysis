import streamlit as st
import pandas as pd
import os

st.title('Exámenes de Admisión UNMSM (2024 - 2025)')
st.divider()

# Layout for option selection
st.header('Hola')

with st.sidebar:
    # Get the folder names of the years in the data/raw folder
    years_list = os.listdir('data/raw')

    year_option = st.selectbox(
        'Año del examen de admisión:',
        years_list,
        placeholder='Seleccione el año'
    )

    # Get careers for the selected year
    filepath = os.listdir(f'data/raw/{year_option}')
    careers_list = [ file.split(".csv")[0].split(f"{year_option}-")[1] for file in filepath ]

    career_option = st.selectbox(
        'Carrera profesional:',
        careers_list,
        index=None,
        placeholder='Seleccione la carrera'
    )