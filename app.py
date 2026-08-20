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
        aging_chart = px.bar(
            aging_summary,
            x="Rango de añejamiento",
            y="Defectos",
            color="estado",
            barmode="group",
            text="Defectos",
            category_orders={
                "Rango de añejamiento": aging_order,
                "estado": ["Fallido", "Bloqueado"],
            },
            color_discrete_map={
                "Fallido": STATUS_COLORS["Fallido"],
                "Bloqueado": STATUS_COLORS["Bloqueado"],
            },
        )
        aging_chart.update_traces(
            textposition="outside",
            hovertemplate=(
                "<b>%{x}</b><br>Resultado: %{fullData.name}<br>"
                "Defectos: %{y}<extra></extra>"
            ),
        )
        aging_chart.update_layout(
            height=360,
            xaxis_title="Antigüedad desde la fecha de ejecución",
            yaxis_title="Cantidad de defectos",
            legend_title_text="Caso vinculado",
            margin=dict(l=10, r=10, t=10, b=10),
        )
        st.plotly_chart(aging_chart, use_container_width=True)
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
