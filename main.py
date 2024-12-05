import streamlit as st
import pandas as pd
import os
import altair as alt
import pathlib

# Set page config
st.set_page_config(page_title="Exámenes de Admisión UNMSM - Dashboard", page_icon=":school:", layout="wide")

# Set styles
# with open("styles.css") as f:
#     st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def load_css(file_path):
    with open(file_path) as f:
        st.html(f"<style>{f.read()}</style>")

css_path = pathlib.Path("styles.css")
load_css(css_path)

@st.cache_data
def load_dataframe(year, career):
    filepath = f"data/processed/{year}/{year}-{career}.csv"
    return pd.read_csv(filepath)

@st.cache_data
def generate_analysis(df, analysis_type="general"):
    
    total_applicants = df.shape[0]
    n_direct_passed_students = df[df["observacion"] == "ALCANZO VACANTE" ].shape[0]
    n_second_choice_students = df[df["observacion"] == "ALCANZO VACANTE SEGUNDA OPCIÓN" ].shape[0]
    n_approved_students = n_direct_passed_students + n_second_choice_students
    n_failed_students = df["observacion"].isna().sum()
    n_absent_students = df[ df["observacion"] == "AUSENTE"].shape[0]

    if analysis_type == "general":
        new_df = pd.DataFrame({
            "observacion": ["ALCANZO VACANTE", "NO ALCANZO VACANTE", "AUSENTE"],
            "count": [n_approved_students, n_failed_students, n_absent_students]
        })

        bars = alt.Chart(new_df).mark_bar().encode(
            x=alt.X("count:Q", title="Número de estudiantes"),
            y=alt.Y("observacion:N", title=""),
            color=alt.Color("observacion", legend=None),
        )

        text = bars.mark_text(
            align="left",
            baseline="middle",
            dx=3
        ).encode(
            text="count"
        )

        return (bars + text).properties(height=200, title="Distribución de estudiantes por estado de admisión")

    elif analysis_type == "kpis":
        pass_rate = n_approved_students / total_applicants
        fail_rate = n_failed_students / total_applicants
        abs_rate = n_absent_students / total_applicants
        top_score = df["puntaje"].max()
        min_direct_passed_score = df[ df["observacion"] == "ALCANZO VACANTE" ]["puntaje"].min()

        return {
            "Tasa de ingreso": pass_rate,
            "Tasa de desaprobación": fail_rate,
            "Tasa de ausencia": abs_rate,
            "Puntaje máximo": top_score,
            "Puntaje mínimo para aprobar": min_direct_passed_score
        }

    elif analysis_type == "score_range":
        pass

    else:
        raise ValueError(f"Invalid analysis type: {analysis_type}")


with st.sidebar:
    years_list = os.listdir('data/processed')
    year_option = st.selectbox('Año del examen de admisión:', years_list, placeholder='Seleccione el año')

    filepath = os.listdir(f'data/processed/{year_option}')
    careers_list = [file.split(".csv")[0].split(f"{year_option}-")[1] for file in filepath]

    career_option = st.selectbox(
        'Carrera profesional:',
        careers_list,
        placeholder='Seleccione la carrera'
    )

st.subheader(f"{year_option} | {career_option}")

try:
    df = load_dataframe(year_option, career_option)

except FileNotFoundError:
    st.info("No se ha encontrado algún archivo.")

cols = st.columns(5)
metrics = generate_analysis(df, analysis_type="kpis")

for i, (key, value) in enumerate(metrics.items()):
    with cols[i]:
        with st.container(border=True):
            if key in ["Tasa de ingreso", "Tasa de desaprobación", "Tasa de ausencia"]:
                st.metric(label=key, value=f"{value:.2%}")
            else:
                st.metric(label=key, value=value)


        

with st.container(border=True):
    # if "df" in locals():
    chart = generate_analysis(df, analysis_type="general")
    st.altair_chart(chart, theme="streamlit", use_container_width=True)