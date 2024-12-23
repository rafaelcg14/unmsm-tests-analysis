import altair as alt

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

def generate_bar_chart(df, x, y, x_axis_title, y_axis_title, title="", height=180):
    bars = alt.Chart(df).mark_bar().encode(
        x=alt.X(x, title=x_axis_title),
        y=alt.Y(y, title=y_axis_title),
        color=alt.Color("observacion", legend=None),
    )

    text = bars.mark_text(
        align="left",
        baseline="middle",
        dx=3
    ).encode(
        text="count"
    )

    bar_chart = (bars + text).properties(height=height, title=title)

    return bar_chart