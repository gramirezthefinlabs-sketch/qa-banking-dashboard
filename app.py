from math import sqrt
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from scipy.stats import chi2_contingency


st.set_page_config(
    page_title="QA Banking Dashboard",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_PATH = Path(__file__).parent / "data" / "casos_prueba_banco_ficticio.csv"
BRAND_BLUE = "#0B5D7A"
BRAND_DARK_BLUE = "#083B55"
BRAND_YELLOW = "#F4B223"
BRAND_LIGHT_BLUE = "#F3F8FB"
STATUS_COLORS = {
    "Aprobado": "#16a34a",
    "Fallido": "#dc2626",
    "Bloqueado": "#f59e0b",
    "No ejecutado": "#64748b",
}
PRIORITY_LABELS = {
    "Crítica": "1-Crítica",
    "Alta": "2-Alta",
    "Media": "3-Media",
    "Baja": "4-Baja",
}


def load_data() -> pd.DataFrame:
    data = pd.read_csv(DATA_PATH, parse_dates=["fecha_ejecucion"])
    data["prioridad"] = data["prioridad"].replace(PRIORITY_LABELS)
    return data


def options(column: str) -> list[str]:
    return sorted(df[column].dropna().unique().tolist())


def metric_card(label: str, value: str, help_text: str) -> None:
    st.metric(label=label, value=value, help=help_text)


st.markdown(
    """
    <style>
    .stApp {background: #F3F8FB;}
    [data-testid="stSidebar"] {background: #083B55;}
    [data-testid="stSidebar"] * {color: #ffffff;}
    [data-testid="stSidebar"] h1 {color: #F4B223;}
    [data-testid="stSidebar"] [data-baseweb="select"] > div,
    [data-testid="stSidebar"] [data-baseweb="input"] > div {
        background: #0B5D7A; border-color: #3A86A2;
    }
    [data-testid="stSidebar"] [data-baseweb="tag"] {
        background: #16779A; border: 1px solid #65AEC5;
    }
    [data-testid="stSidebar"] [data-baseweb="tag"] span,
    [data-testid="stSidebar"] input {color: #ffffff !important;}
    [data-testid="stSidebar"] [data-baseweb="select"] svg,
    [data-testid="stSidebar"] [data-baseweb="tag"] svg {fill: #F4B223;}
    [data-testid="stSidebar"] .st-key-module_filter [data-baseweb="tag"] {
        background: #F4B223 !important; border-color: #F4B223 !important;
    }
    [data-testid="stSidebar"] .st-key-module_filter [data-baseweb="tag"] span {
        color: #083B55 !important; font-weight: 600;
    }
    [data-testid="stSidebar"] .st-key-module_filter [data-baseweb="tag"] svg {
        fill: #083B55 !important;
    }
    .gjemar-logo {
        background: #ffffff; border-radius: 10px; padding: 12px;
        margin-bottom: .7rem; text-align: center;
        box-shadow: 0 3px 10px rgba(0,0,0,.18);
        font-family: Arial, sans-serif; line-height: 1;
    }
    .gjemar-logo .gje, .gjemar-logo .ar {
        color: #0B5D7A !important; font-size: 2.35rem; font-weight: 800;
        letter-spacing: .03em;
    }
    .gjemar-logo .m {
        color: #F4B223 !important; font-size: 2.35rem; font-weight: 800;
        letter-spacing: .03em;
    }
    .gjemar-logo .tagline {
        color: #0B5D7A !important; font-size: .58rem; font-weight: 700;
        letter-spacing: .13em; margin-top: .35rem;
    }
    [data-testid="stMetric"] {
        background: white; border: 1px solid #D6E5EC; border-top: 3px solid #F4B223;
        border-radius: 12px; padding: 14px 16px;
        box-shadow: 0 2px 8px rgba(8,59,85,.08);
    }
    [data-testid="stMetricValue"] {color: #0B5D7A;}
    h1, h2, h3, h4 {color: #083B55;}
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #0B5D7A; border-bottom-color: #F4B223;
    }
    .block-container {padding-top: 1.7rem; padding-bottom: 2rem;}
    .dashboard-note {
        border-left: 4px solid #F4B223; background: #FFF7DF; color: #083B55;
        padding: .7rem 1rem; border-radius: 6px; margin-bottom: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

df = load_data()

with st.sidebar:
    st.markdown(
        '<div class="gjemar-logo"><span class="gje">GJE</span>'
        '<span class="m">M</span><span class="ar">AR</span>'
        '<div class="tagline">QUALITY · DATA · INNOVATION</div></div>',
        unsafe_allow_html=True,
    )
    st.title("🏦 Filtros QA")
    st.caption("Banco ficticio · Datos demostrativos")
    selected_modules = st.multiselect(
        "Módulo",
        options("modulo"),
        default=options("modulo"),
        key="module_filter",
    )
    selected_statuses = st.multiselect("Estado", options("estado"), default=options("estado"))
    selected_priorities = st.multiselect("Prioridad", options("prioridad"), default=options("prioridad"))
    selected_environments = st.multiselect("Ambiente", options("ambiente"), default=options("ambiente"))
    selected_releases = st.multiselect("Release", options("release"), default=options("release"))
    min_date = df["fecha_ejecucion"].min().date()
    max_date = df["fecha_ejecucion"].max().date()
    selected_dates = st.date_input("Período", value=(min_date, max_date), min_value=min_date, max_value=max_date)
    st.divider()
    st.caption("Los indicadores cambian al modificar cualquier filtro.")

if len(selected_dates) == 2:
    start_date, end_date = selected_dates
else:
    start_date = end_date = selected_dates[0]

filtered = df[
    df["modulo"].isin(selected_modules)
    & df["estado"].isin(selected_statuses)
    & df["prioridad"].isin(selected_priorities)
    & df["ambiente"].isin(selected_environments)
    & df["release"].isin(selected_releases)
    & df["fecha_ejecucion"].dt.date.between(start_date, end_date)
].copy()

st.title("QA Banking Dashboard")
st.subheader("Control de casos de prueba del banco ficticio NovaBank")
st.markdown(
    '<div class="dashboard-note">Panel académico con datos simulados. No contiene información real de clientes ni del banco.</div>',
    unsafe_allow_html=True,
)

if filtered.empty:
    st.warning("No existen registros para la combinación de filtros seleccionada.")
    st.stop()

total = len(filtered)
executed = filtered[filtered["estado"] != "No ejecutado"]
approved = int((filtered["estado"] == "Aprobado").sum())
failed = int((filtered["estado"] == "Fallido").sum())
blocked = int((filtered["estado"] == "Bloqueado").sum())
critical_defects = int((filtered["severidad_defecto"] == "Crítica").sum())
execution_rate = len(executed) / total if total else 0
pass_rate = approved / len(executed) if len(executed) else 0
evidence_rate = (executed["evidencia"] == "Sí").mean() if len(executed) else 0

row1 = st.columns(5)
with row1[0]:
    metric_card("Casos filtrados", f"{total:,}", "Cantidad total según los filtros activos")
with row1[1]:
    metric_card("Avance de ejecución", f"{execution_rate:.1%}", "Casos ejecutados / casos filtrados")
with row1[2]:
    metric_card("Tasa de aprobación", f"{pass_rate:.1%}", "Aprobados / casos ejecutados")
with row1[3]:
    metric_card("Fallidos y bloqueados", f"{failed + blocked}", "Casos que requieren atención")
with row1[4]:
    metric_card("Defectos críticos", f"{critical_defects}", "Defectos clasificados con severidad crítica")

tab_summary, tab_risk, tab_detail = st.tabs(["📊 Resumen ejecutivo", "⚠️ Riesgo y cobertura", "📋 Detalle de casos"])

with tab_summary:
    left, right = st.columns(2)
    with left:
        st.markdown("#### Distribución por estado")
        ordered = list(STATUS_COLORS)
        status_counts = (
            filtered["estado"]
            .value_counts()
            .reindex(ordered, fill_value=0)
            .rename_axis("Estado")
            .reset_index(name="Casos")
        )
        status_counts["Estado"] = pd.Categorical(
            status_counts["Estado"],
            categories=ordered,
            ordered=True,
        )
        status_counts = status_counts.sort_values("Estado")
        status_chart = px.pie(
            status_counts,
            names="Estado",
            values="Casos",
            color="Estado",
            hole=0.45,
            color_discrete_map=STATUS_COLORS,
        )
        status_chart.update_traces(
            textinfo="label+percent",
            textposition="outside",
            hovertemplate=(
                "<b>%{label}</b><br>Casos: %{value}<br>"
                "Participación: %{percent}<extra></extra>"
            ),
        )
        status_chart.update_layout(
            height=340,
            legend_title_text=None,
            margin=dict(l=10, r=10, t=10, b=10),
            annotations=[
                dict(
                    text=f"<b>{int(status_counts['Casos'].sum())}</b><br>casos",
                    x=0.5,
                    y=0.5,
                    font_size=18,
                    showarrow=False,
                )
            ],
        )
        st.plotly_chart(status_chart, use_container_width=True)
    with right:
        st.markdown("#### Ejecución diaria y línea media")
        daily = (
            executed.groupby("fecha_ejecucion")
            .size()
            .rename("Ejecutados")
            .sort_index()
            .reset_index()
        )
        daily_average = daily["Ejecutados"].mean()
        execution_chart = px.line(
            daily,
            x="fecha_ejecucion",
            y="Ejecutados",
            markers=True,
        )
        execution_chart.update_traces(
            line_color=BRAND_BLUE,
            hovertemplate=(
                "<b>%{x|%d/%m/%Y}</b><br>"
                "Casos ejecutados: %{y}<extra></extra>"
            ),
        )
        execution_chart.add_hline(
            y=daily_average,
            line_dash="dash",
            line_color=BRAND_YELLOW,
            line_width=2,
            annotation_text=f"Media: {daily_average:.1f}",
            annotation_position="top left",
        )
        execution_chart.update_layout(
            height=340,
            xaxis_title="Fecha",
            yaxis_title="Casos ejecutados por día",
            margin=dict(l=10, r=10, t=10, b=10),
        )
        st.plotly_chart(execution_chart, use_container_width=True)

    st.markdown("#### Distribución de resultados por módulo (%)")
    ordered = list(STATUS_COLORS)
    module_status = (
        pd.crosstab(filtered["modulo"], filtered["estado"], normalize="index")
        .reindex(columns=ordered, fill_value=0)
        .mul(100)
    )
    risk_order = (
        module_status.get("Fallido", 0) + module_status.get("Bloqueado", 0)
    ).sort_values(ascending=False).index.tolist()
    module_status_long = (
        module_status.reset_index()
        .melt(id_vars="modulo", var_name="Estado", value_name="Porcentaje")
    )
    module_chart = px.bar(
        module_status_long,
        x="Porcentaje",
        y="modulo",
        color="Estado",
        orientation="h",
        category_orders={
            "modulo": risk_order[::-1],
            "Estado": ordered,
        },
        color_discrete_map=STATUS_COLORS,
    )
    module_chart.update_traces(
        hovertemplate=(
            "<b>%{y}</b><br>Estado: %{fullData.name}<br>"
            "Porcentaje: %{x:.1f}%<extra></extra>"
        ),
    )
    module_chart.update_layout(
        height=380,
        barmode="stack",
        xaxis_title="Porcentaje de casos",
        yaxis_title=None,
        xaxis=dict(range=[0, 100], ticksuffix="%"),
        legend_title_text=None,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        margin=dict(l=10, r=10, t=45, b=10),
    )
    st.plotly_chart(module_chart, use_container_width=True)

with tab_risk:
    st.markdown("#### Añejamiento de defectos vinculados a casos fallidos y bloqueados")
    defect_aging = filtered[
        filtered["estado"].isin(["Fallido", "Bloqueado"])
        & filtered["defecto_id"].notna()
    ].copy()
    if defect_aging.empty:
        st.info("No existen defectos vinculados a casos fallidos o bloqueados para los filtros seleccionados.")
    else:
        reference_date = df["fecha_ejecucion"].max()
        defect_aging["Días de antigüedad"] = (
            reference_date - defect_aging["fecha_ejecucion"]
        ).dt.days.clip(lower=0)
        aging_order = ["0-7 días", "8-15 días", "16-30 días", "Más de 30 días"]
        defect_aging["Rango de añejamiento"] = pd.cut(
            defect_aging["Días de antigüedad"],
            bins=[-1, 7, 15, 30, float("inf")],
            labels=aging_order,
        )
        aging_summary = (
            defect_aging.groupby(
                ["Rango de añejamiento", "estado"],
                observed=True,
            )["defecto_id"]
            .nunique()
            .reset_index(name="Defectos")
        )
        funnel_width = [100, 75, 50, 25]
        failed_counts = (
            aging_summary[aging_summary["estado"] == "Fallido"]
            .set_index("Rango de añejamiento")["Defectos"]
            .reindex(aging_order, fill_value=0)
            .astype(int)
            .tolist()
        )
        blocked_counts = (
            aging_summary[aging_summary["estado"] == "Bloqueado"]
            .set_index("Rango de añejamiento")["Defectos"]
            .reindex(aging_order, fill_value=0)
            .astype(int)
            .tolist()
        )
        stage_totals = [
            failed + blocked
            for failed, blocked in zip(failed_counts, blocked_counts)
        ]
        failed_width = [
            width * failed / total if total else 0
            for width, failed, total in zip(
                funnel_width,
                failed_counts,
                stage_totals,
            )
        ]
        blocked_width = [
            width * blocked / total if total else 0
            for width, blocked, total in zip(
                funnel_width,
                blocked_counts,
                stage_totals,
            )
        ]

        aging_funnel = go.Figure()
        aging_funnel.add_trace(
            go.Funnel(
                name="Fallido",
                y=aging_order,
                x=failed_width,
                customdata=failed_counts,
                texttemplate="<b>%{customdata}</b>",
                hovertemplate=(
                    "<b>%{y}</b><br>Casos fallidos: %{customdata}"
                    "<extra></extra>"
                ),
                marker=dict(color=STATUS_COLORS["Fallido"]),
                connector=dict(line=dict(color="#ffffff", width=1)),
            )
        )
        aging_funnel.add_trace(
            go.Funnel(
                name="Bloqueado",
                y=aging_order,
                x=blocked_width,
                customdata=blocked_counts,
                texttemplate="<b>%{customdata}</b>",
                hovertemplate=(
                    "<b>%{y}</b><br>Casos bloqueados: %{customdata}"
                    "<extra></extra>"
                ),
                marker=dict(color=STATUS_COLORS["Bloqueado"]),
                connector=dict(line=dict(color="#ffffff", width=1)),
            )
        )
        aging_funnel.update_layout(
            height=450,
            funnelmode="stack",
            legend_title_text="Caso vinculado",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5,
            ),
            margin=dict(l=10, r=10, t=55, b=10),
            xaxis=dict(visible=False),
        )
        st.plotly_chart(aging_funnel, use_container_width=True)
        st.caption(
            "El ancho representa el avance del añejamiento y cada nivel mezcla "
            "los defectos de casos fallidos y bloqueados. Las cifras muestran "
            "la cantidad real de defectos."
        )
        st.caption(
            f"Fecha de referencia: {reference_date:%d/%m/%Y}. "
            "La fecha de ejecución se utiliza como fecha de reporte del defecto."
        )
        st.markdown("##### Referencias de defectos por antigüedad")
        selected_aging_range = st.selectbox(
            "Rango de antigüedad",
            ["Todos"] + aging_order,
            key="aging_range_filter",
        )
        aging_detail = defect_aging.copy()
        if selected_aging_range != "Todos":
            aging_detail = aging_detail[
                aging_detail["Rango de añejamiento"] == selected_aging_range
            ]
        aging_detail["Rango de antigüedad"] = (
            aging_detail["Rango de añejamiento"].astype(str)
        )
        aging_detail = (
            aging_detail[
                [
                    "defecto_id",
                    "Días de antigüedad",
                    "Rango de antigüedad",
                    "caso_id",
                    "estado",
                    "modulo",
                    "severidad_defecto",
                    "fecha_ejecucion",
                ]
            ]
            .drop_duplicates(subset=["defecto_id"])
            .sort_values(
                ["Días de antigüedad", "defecto_id"],
                ascending=[False, True],
            )
            .rename(
                columns={
                    "defecto_id": "Referencia del defecto",
                    "caso_id": "Caso vinculado",
                    "estado": "Resultado del caso",
                    "modulo": "Módulo",
                    "severidad_defecto": "Severidad",
                    "fecha_ejecucion": "Fecha de reporte",
                }
            )
        )
        st.dataframe(
            aging_detail,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Fecha de reporte": st.column_config.DateColumn(
                    "Fecha de reporte",
                    format="DD/MM/YYYY",
                ),
                "Días de antigüedad": st.column_config.NumberColumn(
                    "Días de antigüedad",
                    format="%d días",
                ),
            },
        )


    st.markdown("#### Asociación del riesgo con prioridad o ambiente")
    analysis_variable = st.selectbox(
        "Variable para analizar",
        ["Prioridad", "Ambiente"],
        key="risk_association_variable",
    )
    analysis_column = {
        "Prioridad": "prioridad",
        "Ambiente": "ambiente",
    }[analysis_variable]
    risk_records = filtered[filtered["defecto_id"].notna()].copy()

    if risk_records.empty:
        st.info("No existen defectos para realizar el análisis de asociación.")
    else:
        contingency = pd.crosstab(
            risk_records[analysis_column],
            risk_records["severidad_defecto"],
        )
        severity_order = ["Crítica", "Alta", "Media", "Baja"]
        contingency = contingency.reindex(
            columns=severity_order,
            fill_value=0,
        )
        if analysis_variable == "Prioridad":
            contingency = contingency.reindex(
                list(PRIORITY_LABELS.values()),
                fill_value=0,
            )
        else:
            contingency = contingency.sort_index()

        contingency = contingency.loc[
            contingency.sum(axis=1) > 0,
            contingency.sum(axis=0) > 0,
        ]
        heatmap_values = (
            contingency.div(contingency.sum(axis=1), axis=0) * 100
        ).round(1)
        association_heatmap = px.imshow(
            heatmap_values,
            text_auto=".1f",
            aspect="auto",
            color_continuous_scale=[
                [0.0, "#EAF4F8"],
                [0.5, "#6FA9BD"],
                [1.0, "#F4B223"],
            ],
            labels={
                "x": "Severidad del defecto",
                "y": analysis_variable,
                "color": "Distribución %",
            },
        )
        association_heatmap.update_traces(
            texttemplate="%{z:.1f}%",
            hovertemplate=(
                f"<b>{analysis_variable}: %{{y}}</b><br>"
                "Severidad: %{x}<br>Distribución: %{z:.1f}%"
                "<extra></extra>"
            ),
        )
        association_heatmap.update_layout(
            height=360,
            margin=dict(l=10, r=10, t=10, b=10),
        )
        st.plotly_chart(association_heatmap, use_container_width=True)

        if contingency.shape[0] >= 2 and contingency.shape[1] >= 2:
            chi2_value, p_value, degrees_freedom, _ = chi2_contingency(
                contingency
            )
            observations = contingency.to_numpy().sum()
            minimum_dimension = min(
                contingency.shape[0] - 1,
                contingency.shape[1] - 1,
            )
            cramers_v = (
                sqrt(chi2_value / (observations * minimum_dimension))
                if observations and minimum_dimension
                else 0.0
            )
            if cramers_v < 0.10:
                association_strength = "muy débil"
            elif cramers_v < 0.30:
                association_strength = "débil"
            elif cramers_v < 0.50:
                association_strength = "moderada"
            else:
                association_strength = "fuerte"

            chi_col, p_col, v_col = st.columns(3)
            with chi_col:
                st.metric("Chi-cuadrada", f"{chi2_value:.2f}")
            with p_col:
                st.metric("Valor p", f"{p_value:.4f}")
            with v_col:
                st.metric("V de Cramér", f"{cramers_v:.3f}")

            if p_value < 0.05:
                st.success(
                    f"Existe una asociación estadísticamente significativa "
                    f"entre severidad y {analysis_variable.lower()} "
                    f"(p < 0.05). La fuerza es {association_strength}."
                )
            else:
                st.info(
                    f"No se encontró una asociación estadísticamente "
                    f"significativa entre severidad y "
                    f"{analysis_variable.lower()} (p ≥ 0.05)."
                )
            st.caption(
                f"Prueba Chi-cuadrada con {degrees_freedom} grados de libertad. "
                "La V de Cramér mide la fuerza de asociación entre variables "
                "categóricas."
            )
        else:
            st.warning(
                "Se requieren al menos dos categorías por variable para "
                "calcular Chi-cuadrada."
            )


    st.markdown("#### Boxplot de criticidad en casos fallidos y bloqueados")
    attention_box = filtered[
        filtered["estado"].isin(["Fallido", "Bloqueado"])
    ].copy()
    if attention_box.empty:
        st.info("No existen casos fallidos o bloqueados para construir el boxplot.")
    else:
        criticality_score = {
            "1-Crítica": 4,
            "2-Alta": 3,
            "3-Media": 2,
            "4-Baja": 1,
        }
        attention_box["Puntuación de criticidad"] = (
            attention_box["prioridad"].map(criticality_score)
        )
        criticality_boxplot = px.box(
            attention_box,
            x="estado",
            y="Puntuación de criticidad",
            color="estado",
            points="all",
            category_orders={
                "estado": ["Fallido", "Bloqueado"],
            },
            color_discrete_map={
                "Fallido": STATUS_COLORS["Fallido"],
                "Bloqueado": STATUS_COLORS["Bloqueado"],
            },
            hover_name="caso_id",
            hover_data={
                "prioridad": True,
                "modulo": True,
                "estado": False,
                "Puntuación de criticidad": False,
            },
        )
        criticality_boxplot.update_traces(
            jitter=0.30,
            pointpos=0,
            marker=dict(size=7, opacity=0.65),
        )
        criticality_boxplot.update_layout(
            height=410,
            xaxis_title="Resultado del caso",
            yaxis_title="Nivel de criticidad",
            showlegend=False,
            margin=dict(l=10, r=10, t=10, b=10),
        )
        criticality_boxplot.update_yaxes(
            tickmode="array",
            tickvals=[1, 2, 3, 4],
            ticktext=["1 · Baja", "2 · Media", "3 · Alta", "4 · Crítica"],
            range=[0.5, 4.5],
        )
        st.plotly_chart(criticality_boxplot, use_container_width=True)

        outlier_counts = {}
        for case_status, status_group in attention_box.groupby("estado"):
            first_quartile = status_group[
                "Puntuación de criticidad"
            ].quantile(0.25)
            third_quartile = status_group[
                "Puntuación de criticidad"
            ].quantile(0.75)
            interquartile_range = third_quartile - first_quartile
            lower_limit = first_quartile - 1.5 * interquartile_range
            upper_limit = third_quartile + 1.5 * interquartile_range
            outlier_counts[case_status] = int(
                (
                    (
                        status_group["Puntuación de criticidad"]
                        < lower_limit
                    )
                    |
                    (
                        status_group["Puntuación de criticidad"]
                        > upper_limit
                    )
                ).sum()
            )
        st.caption(
            "Outliers según el método IQR (1.5 × rango intercuartílico): "
            f"Fallidos: {outlier_counts.get('Fallido', 0)} · "
            f"Bloqueados: {outlier_counts.get('Bloqueado', 0)}."
        )


    a, b = st.columns(2)
    with a:
        st.markdown("#### Casos de atención por prioridad")
        attention = filtered[filtered["estado"].isin(["Fallido", "Bloqueado"])]
        risk_matrix = pd.crosstab(attention["prioridad"], attention["estado"])
        st.dataframe(risk_matrix, use_container_width=True)
    with b:
        st.markdown("#### Calidad de evidencia")
        metric_card("Casos ejecutados con evidencia", f"{evidence_rate:.1%}", "Evidencia = Sí / casos ejecutados")
        missing_evidence = executed[executed["evidencia"] == "No"]
        st.write(f"Casos ejecutados sin evidencia: **{len(missing_evidence)}**")
        st.write(f"Casos automatizados: **{(filtered['automatizado'] == 'Sí').mean():.1%}**")

    st.markdown("#### Priorización de módulos")
    risk_by_module = (
        filtered.assign(
            requiere_atencion=filtered["estado"].isin(["Fallido", "Bloqueado"]).astype(int),
            critico=(filtered["severidad_defecto"] == "Crítica").astype(int),
        )
        .groupby("modulo")
        .agg(
            Casos=("caso_id", "count"),
            **{
                "Casos fallidos y bloqueados": ("requiere_atencion", "sum"),
                "Defectos críticos": ("critico", "sum"),
            },
        )
    )
    risk_by_module["Riesgo %"] = (
        risk_by_module["Casos fallidos y bloqueados"] / risk_by_module["Casos"] * 100
    ).round(1)
    risk_by_module = risk_by_module.sort_values(
        ["Defectos críticos", "Riesgo %"], ascending=False
    )
    st.dataframe(risk_by_module, use_container_width=True)

with tab_detail:
    st.markdown("#### Registros filtrados")
    search = st.text_input("Buscar por ID, nombre, módulo o defecto", placeholder="Ejemplo: TC-0025 o DEF-1025")
    detail = filtered.copy()
    if search:
        mask = detail.astype(str).apply(lambda col: col.str.contains(search, case=False, na=False)).any(axis=1)
        detail = detail[mask]
    st.dataframe(
        detail.sort_values(["fecha_ejecucion", "caso_id"], ascending=[False, True]),
        use_container_width=True,
        hide_index=True,
        column_config={"fecha_ejecucion": st.column_config.DateColumn("Fecha", format="DD/MM/YYYY")},
    )
    st.download_button(
        "⬇️ Descargar resultados filtrados",
        data=detail.to_csv(index=False).encode("utf-8-sig"),
        file_name="casos_prueba_filtrados.csv",
        mime="text/csv",
    )

st.caption("Proyecto académico · Python + Streamlit · Datos ficticios generados para fines educativos")
