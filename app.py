from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(
    page_title="QA Banking Dashboard",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_PATH = Path(__file__).parent / "data" / "casos_prueba_banco_ficticio.csv"
STATUS_COLORS = {
    "Aprobado": "#16a34a",
    "Fallido": "#dc2626",
    "Bloqueado": "#f59e0b",
    "No ejecutado": "#64748b",
}


@st.cache_data
def load_data() -> pd.DataFrame:
    data = pd.read_csv(DATA_PATH, parse_dates=["fecha_ejecucion"])
    return data


def options(column: str) -> list[str]:
    return sorted(df[column].dropna().unique().tolist())


def metric_card(label: str, value: str, help_text: str) -> None:
    st.metric(label=label, value=value, help=help_text)


st.markdown(
    """
    <style>
    .stApp {background: #f5f7fb;}
    [data-testid="stSidebar"] {background: #102a43;}
    [data-testid="stSidebar"] * {color: #ffffff;}
    [data-testid="stMetric"] {
        background: white; border: 1px solid #dbe4ee; border-radius: 12px;
        padding: 14px 16px; box-shadow: 0 2px 8px rgba(16,42,67,.06);
    }
    .block-container {padding-top: 1.7rem; padding-bottom: 2rem;}
    .dashboard-note {
        border-left: 4px solid #1f8a8a; background: #eaf7f7; color: #123;
        padding: .7rem 1rem; border-radius: 6px; margin-bottom: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

df = load_data()

with st.sidebar:
    st.title("🏦 Filtros QA")
    st.caption("Banco ficticio · Datos demostrativos")
    selected_modules = st.multiselect("Módulo", options("modulo"), default=options("modulo"))
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
        status_chart = px.bar(
            status_counts,
            x="Estado",
            y="Casos",
            color="Estado",
            text="Casos",
            category_orders={"Estado": ordered},
            color_discrete_map=STATUS_COLORS,
        )
        status_chart.update_traces(
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Casos: %{y}<extra></extra>",
        )
        status_chart.update_layout(
            height=340,
            showlegend=False,
            xaxis_title=None,
            yaxis_title="Cantidad de casos",
            margin=dict(l=10, r=10, t=10, b=10),
        )
        st.plotly_chart(status_chart, use_container_width=True)
    with right:
        st.markdown("#### Ejecución acumulada por fecha")
        daily = (
            executed.groupby("fecha_ejecucion").size().rename("Ejecutados").sort_index().cumsum()
            .reset_index()
        )
        execution_chart = px.line(
            daily,
            x="fecha_ejecucion",
            y="Ejecutados",
            markers=True,
        )
        execution_chart.update_traces(
            line_color="#2457a7",
            hovertemplate="<b>%{x|%d/%m/%Y}</b><br>Ejecutados: %{y}<extra></extra>",
        )
        execution_chart.update_layout(
            height=340,
            xaxis_title="Fecha",
            yaxis_title="Casos ejecutados acumulados",
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
    module_chart = px.scatter(
        module_status_long,
        x="Porcentaje",
        y="modulo",
        color="Estado",
        category_orders={
            "modulo": risk_order[::-1],
            "Estado": ordered,
        },
        color_discrete_map=STATUS_COLORS,
    )
    module_chart.update_traces(
        marker=dict(size=13, opacity=0.9),
        hovertemplate=(
            "<b>%{y}</b><br>Estado: %{fullData.name}<br>"
            "Porcentaje: %{x:.1f}%<extra></extra>"
        ),
    )
    module_chart.update_layout(
        height=380,
        xaxis_title="Porcentaje de casos",
        yaxis_title=None,
        xaxis=dict(range=[0, 100], ticksuffix="%"),
        legend_title_text=None,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        margin=dict(l=10, r=10, t=45, b=10),
    )
    st.plotly_chart(module_chart, use_container_width=True)

with tab_risk:
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
        .agg(Casos=("caso_id", "count"), Atención=("requiere_atencion", "sum"), Críticos=("critico", "sum"))
    )
    risk_by_module["Riesgo %"] = (risk_by_module["Atención"] / risk_by_module["Casos"] * 100).round(1)
    risk_by_module = risk_by_module.sort_values(["Críticos", "Riesgo %"], ascending=False)
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
