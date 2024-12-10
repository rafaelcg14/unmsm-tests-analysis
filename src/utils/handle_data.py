import pandas as pd
import streamlit as st
import altair as alt

from src.utils.generate_plots import generate_histogram, generate_boxplot, generate_bar_chart

def load_dataframe(year, career):
    filepath = f"data/processed/{year}/{year}-{career}.csv"

    return pd.read_csv(filepath)

def career_exists_for_year(year, career):
    try:
        temp_df = load_dataframe(year, career)

        return career in temp_df["carrera"].unique()
    
    except FileNotFoundError:
        return False
    
def generate_analysis(df, analysis_type="general", **kwargs):
    career = kwargs.get("career", None)
    
    # Additional dataframes
    direct_passed_students = df[ df["observacion"].isin(["ALCANZO VACANTE", "ALCANZO VACANTE PRIMERA OPCIÓN"]) ]
    second_choice_students = df[ df["segunda_opcion"] == career ]
    approved_students = pd.concat([direct_passed_students, second_choice_students])

    # Get desired metrics
    total_applicants = df[ df["carrera"] == career ].shape[0]
    n_approved_students = approved_students.shape[0]
    n_failed_students = df["observacion"].isna().sum()
    n_absent_students = df[ df["observacion"] == "AUSENTE"].shape[0]

    if analysis_type == "general":
        new_df = pd.DataFrame({
            "observacion": ["ALCANZÓ VACANTE", "NO ALCANZÓ VACANTE", "AUSENTE"],
            "count": [n_approved_students, n_failed_students, n_absent_students]
        })

        general_analysis_chart = generate_bar_chart(
            new_df,
            x="count:Q",
            y="observacion:N",
            x_axis_title="Número de postulantes",
            y_axis_title="",
            title="Distribución de postulantes por estado de admisión",
            height=180
        )

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
        dataframes = kwargs.get("dataframes", None)

        df_direct_passed = {
            year: dataframes[year][dataframes[year]["observacion"].isin(["ALCANZO VACANTE", "ALCANZO VACANTE PRIMERA OPCIÓN"])]
            for year in dataframes.keys()
        }
        df_second_choice = {
            year: dataframes[year][dataframes[year]["segunda_opcion"] == career]
            for year in dataframes.keys()
        }
        df_approved = {
            year: pd.concat([df_direct_passed[year], df_second_choice[year]])
            for year in dataframes.keys()
        }

        # Find max, min and mean values
        max_scores = {}
        min_scores = {}
        mean_scores = {}

        for year, df in df_approved.items():
            if not df.empty:
                max_scores[year] = df["puntaje"].max()
                min_scores[year] = df["puntaje"].min()
                mean_scores[year] = df["puntaje"].mean()
            else:
                max_scores[year] = None
                min_scores[year] = None
                mean_scores[year] = None

        # New dataframe for computed scores filtering years out with any values
        trend_df = pd.DataFrame({
            "Año": list(dataframes.keys()),
            "Máximo": list(max_scores.values()),
            "Mínimo": list(min_scores.values()),
            "Promedio": list(mean_scores.values())
        }).dropna( subset=["Máximo", "Mínimo", "Promedio"] )

        # Reshape to long format
        trend_df = trend_df.melt(id_vars="Año", var_name="Tipo de puntaje", value_name="Puntaje")

        # Plot the trend using Altair
        trend_chart = alt.Chart(trend_df).mark_line(point=True).encode(
            x=alt.X("Año:N", title="", axis=alt.Axis(labelAngle=0)),
            y=alt.Y("Puntaje:Q", title="Puntaje", scale=alt.Scale(zero=False)),
            color=alt.Color("Tipo de puntaje:N", title="Tipo de puntaje"),
            tooltip=["Año", "Tipo de puntaje", "Puntaje"]
        ).properties(
            title=f"Tendencia de puntajes de ingreso",
            height=250
        )

        return trend_chart
        
    else:
        raise ValueError(f"Invalid analysis type: {analysis_type}")