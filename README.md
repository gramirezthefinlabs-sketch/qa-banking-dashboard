# QA Banking Dashboard

Dashboard interactivo para analizar casos de prueba de **NovaBank**, un banco completamente ficticio. El proyecto utiliza datos sintéticos y no contiene información real de clientes o instituciones financieras.

## Funcionalidades

- Filtros por módulo, estado, prioridad, ambiente, release y fecha.
- KPIs dinámicos de avance, aprobación, fallos, bloqueos y defectos críticos.
- Distribución de estados y tendencia acumulada de ejecución.
- Comparación de resultados por módulo.
- Priorización de riesgos y control de evidencias.
- Buscador y descarga de los registros filtrados.

## Ejecutar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Estructura

```text
qa_banking_dashboard/
├── app.py
├── data/
│   └── casos_prueba_banco_ficticio.csv
├── generate_data.py
├── README.md
└── requirements.txt
```

Para reconstruir la base de datos sintética:

```bash
python generate_data.py
```

## Publicación

El repositorio puede desplegarse en Streamlit Community Cloud seleccionando `app.py` como archivo principal.
