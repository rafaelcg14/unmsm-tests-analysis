import streamlit as st
import pandas as pd
import os
import altair as alt
import pathlib

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
def load_dataframe(year, career):
    filepath = f"data/processed/{year}/{year}-{career}.csv"
    return pd.read_csv(filepath)

def generate_histogram(df, x: str, y: str, x_axis_title: str, y_axis_title: str, title="", maxbins=10, field_legend="", height=300):
    hist = alt.Chart(df).mark_bar().encode(
        x=alt.X(x, title=x_axis_title, bin=True).bin(maxbins=maxbins),
        y=alt.Y(y, title=y_axis_title),
        color=alt.Color(field_legend, legend=alt.Legend(title="", orient="top-right", direction="horizontal"))
    ).properties(
        title=title,
        height=height
    )

    return hist

def generate_boxplot(df, x: str, y: str, x_axis_title: str, y_axis_title: str, title="", height=300, field_legend=""):
    boxplot = alt.Chart(df).mark_boxplot(extent="min-max", color="white").encode(
        x=alt.X(x, title=x_axis_title).scale(zero=False),
        y=alt.Y(y, title=y_axis_title),
        color=alt.Color(field_legend, legend=None)
    ).properties(
        title=title,
        height=height
    )

    return boxplot

@st.cache_data
def generate_analysis(df, analysis_type="general", **kwargs):
    career = kwargs.get("career", None)
    
    # Additional dataframes
    direct_passed_students = df[ df["observacion"].isin(["ALCANZO VACANTE", "ALCANZO VACANTE PRIMERA OPCIÓN"]) ]
    second_choice_students = df[ df["segunda_opcion"] == career ]
    approved_students = pd.concat([direct_passed_students, second_choice_students])

    # Get desired metrics
    total_applicants = df[ df["carrera"] == career ].shape[0]
    n_direct_passed_students = direct_passed_students.shape[0]
    n_second_choice_students = second_choice_students.shape[0]
    n_approved_students = approved_students.shape[0]
    n_failed_students = df["observacion"].isna().sum()
    n_absent_students = df[ df["observacion"] == "AUSENTE"].shape[0]

    if analysis_type == "general":
        new_df = pd.DataFrame({
            "observacion": ["ALCANZÓ VACANTE", "NO ALCANZÓ VACANTE", "AUSENTE"],
            "count": [n_approved_students, n_failed_students, n_absent_students]
        })

        bars = alt.Chart(new_df).mark_bar().encode(
            x=alt.X("count:Q", title="Número de postulantes"),
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

        general_analysis_chart = (bars + text).properties(height=180, title="Distribución de postulantes por estado de admisión")

        return general_analysis_chart

    elif analysis_type == "kpis":
        top_score = df["puntaje"].max()
        min_direct_passed_score = df[df["observacion"].isin(["ALCANZO VACANTE", "ALCANZO VACANTE PRIMERA OPCIÓN"]) ]["puntaje"].min()
        mean_approved_score = approved_students["puntaje"].mean().round()

        return {
            "Número de postulantes": total_applicants,
            "Puntaje máximo": top_score,
            "Puntaje promedio de ingreso": mean_approved_score,
            "Puntaje mínimo para ingresar": min_direct_passed_score
        }

    elif analysis_type == "score_range":

        # Histogram of total students
        scores_hist_df = df[["puntaje", "observacion"]]
        scores_hist_df["observacion"] = scores_hist_df["observacion"].fillna("NO ALCANZÓ VACANTE")
        scores_hist_df = scores_hist_df.dropna(subset=["puntaje"])
        scores_hist_df["observacion"] = scores_hist_df["observacion"].replace({
            "ALCANZO VACANTE" and "ALCANZO VACANTE PRIMERA OPCIÓN": "ALCANZO VACANTE",
            "ALCANZO VACANTE SEGUNDA OPCIÓN": "ALCANZO VACANTE",
            "NO ALCANZÓ VACANTE": "NO ALCANZÓ VACANTE"
        })

        hist1 = generate_histogram(
            scores_hist_df,
            x="puntaje:Q",
            y="count():Q",
            x_axis_title="Puntaje",
            y_axis_title="Número de postulantes",
            title="",
            maxbins=40,
            field_legend="observacion",
            height=400
        )

        bp1 = generate_boxplot(
            scores_hist_df,
            x="puntaje:Q",
            y="observacion:N",
            x_axis_title="Puntaje",
            y_axis_title="",
            title="Distribución de puntajes del total de postulantes",
            height=200,
            field_legend="observacion"
        )

        # Histogram with approved students
        scores_df = approved_students[["puntaje", "observacion"]]
        scores_df["observacion"] = scores_df["observacion"].replace({
            "ALCANZO VACANTE" and "ALCANZO VACANTE PRIMERA OPCIÓN": "ALCANZO VACANTE",
            "ALCANZO VACANTE SEGUNDA OPCIÓN": "SEGUNDA OPCIÓN",
        })

        hist2 = generate_histogram(
            scores_df,
            x="puntaje:Q",
            y="count():Q",
            x_axis_title="Puntaje",
            y_axis_title="Número de postulantes",
            title="",
            maxbins=20,
            field_legend="observacion",
            height=400
        )

        bp2 = generate_boxplot(
            scores_df,
            x="puntaje:Q",
            y="observacion:N",
            x_axis_title="Puntaje",
            y_axis_title="",
            title="Distribución de puntajes de postulantes que ingresaron",
            height=200,
            field_legend="observacion"
        )

        return hist1, hist2, bp1, bp2
    
    elif analysis_type == "top_10_scores":
        top_10_scores = approved_students.sort_values("puntaje", ascending=False).loc[:, "puntaje"].head(10).reset_index(drop=True)
        top_10_scores.index = top_10_scores.index + 1
        top_10_scores.index.name = "Posición"
        top_10_scores.name = "Puntaje"
        
        st.dataframe(
            top_10_scores,
            width=500,
            column_config={
                "Posición": st.column_config.TextColumn(
                        "#",
                ),
                "Puntaje": st.column_config.ProgressColumn(
                    "Puntaje",
                    format="%f",
                    min_value=600,
                    max_value=max(top_10_scores)
                )
            }
        )

    elif analysis_type == "trend_over_years":
        

        pass
        
        


    else:
        raise ValueError(f"Invalid analysis type: {analysis_type}")

# Sidebar
# TODO: Add pages to sidebar



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
    df = load_dataframe(year_option, career_option)

    # Create a dictionary of dataframes with the years as keys and the dataframes as values for the career of each year selected
    dataframes = {year: load_dataframe(year, career_option) for year in years_list}

except FileNotFoundError:
    st.info("No se ha encontrado algún archivo.")


# Display dashboard
cols = st.columns(4)

metrics = generate_analysis(df, analysis_type="kpis", career=career_option)

for i, key, value in zip(range(4), metrics.keys(), metrics.values()):
    with cols[i]:
        with st.container(border=True):
            st.metric(label=key, value=value)
            


cols = st.columns([3, 1])

with cols[0]:
    with st.container(border=True):
        # if "df" in locals():
        general_analysis_chart = generate_analysis(df, analysis_type="general", career=career_option)
        st.altair_chart(general_analysis_chart, theme="streamlit", use_container_width=True)

        # trend_chart = generate_analysis(df, analysis_type="trend_over_years", career=career_option)
        # st.altair_chart(trend_chart, theme="streamlit", use_container_width=True)
    
with cols[1]:
    with st.container(border=True):
        st.write("##### Top 10 puntajes")
        generate_analysis(df, analysis_type="top_10_scores", career=career_option)

cols = st.columns(2)

hist1, hist2, bp1, bp2 = generate_analysis(df, analysis_type="score_range", career=career_option)

with cols[0]:
    with st.container(border=True):
        st.altair_chart(bp1, theme="streamlit", use_container_width=True)
        st.altair_chart(hist1, theme="streamlit", use_container_width=True)

with cols[1]:
    with st.container(border=True):
        st.altair_chart(bp2, theme="streamlit", use_container_width=True)
        st.altair_chart(hist2, theme="streamlit", use_container_width=True)