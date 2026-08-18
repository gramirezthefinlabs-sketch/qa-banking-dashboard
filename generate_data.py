from __future__ import annotations

import csv
import random
from datetime import date, timedelta
from pathlib import Path


RANDOM_SEED = 20260818
ROWS = 420
MODULES = {
    "Clientes": ["Creación", "Actualización", "Debida diligencia", "Bloqueo"],
    "Cuentas": ["Apertura", "Mantenimiento", "Cargos", "Cierre"],
    "Préstamos": ["Desembolso", "Cuotas", "Pagos", "Reversos"],
    "Pagos": ["ACH", "LBTR", "Pago de servicios", "Reversos"],
    "Transferencias": ["Internas", "Interbancarias", "Límites", "Reversos"],
    "Tarjetas": ["Emisión", "Consumos", "Bloqueo", "Pagos"],
}
TEST_TYPES = ["Funcional", "Integración", "Regresión", "API", "Seguridad", "COB/EOD"]
PRIORITIES = ["Crítica", "Alta", "Media", "Baja"]
ENVIRONMENTS = ["QA", "SIT", "UAT"]
RELEASES = ["R25.1", "R25.2", "R25.3"]
TESTERS = ["Ana", "Carlos", "Elena", "José", "Laura", "Miguel"]


def weighted_choice(rng: random.Random, values: list[str], weights: list[int]) -> str:
    return rng.choices(values, weights=weights, k=1)[0]


def build_rows() -> list[dict[str, object]]:
    rng = random.Random(RANDOM_SEED)
    start = date(2026, 7, 1)
    records: list[dict[str, object]] = []

    for index in range(1, ROWS + 1):
        module = rng.choice(list(MODULES))
        priority = weighted_choice(rng, PRIORITIES, [12, 31, 39, 18])
        status = weighted_choice(
            rng,
            ["Aprobado", "Fallido", "Bloqueado", "No ejecutado"],
            [63, 16, 7, 14],
        )
        execution_date = start + timedelta(days=rng.randint(0, 47))

        if status == "Fallido":
            severity = weighted_choice(
                rng,
                ["Crítica", "Alta", "Media", "Baja"],
                [11 if priority == "Crítica" else 5, 36, 38, 15],
            )
            defect_id = f"DEF-{1000 + index}"
        elif status == "Bloqueado":
            severity = weighted_choice(rng, ["Alta", "Media"], [65, 35])
            defect_id = f"DEF-{1000 + index}"
        else:
            severity = "Sin defecto"
            defect_id = ""

        records.append(
            {
                "caso_id": f"TC-{index:04d}",
                "nombre_caso": f"Validar {rng.choice(MODULES[module]).lower()} - escenario {index:03d}",
                "modulo": module,
                "subproceso": rng.choice(MODULES[module]),
                "tipo_prueba": rng.choice(TEST_TYPES),
                "prioridad": priority,
                "estado": status,
                "severidad_defecto": severity,
                "defecto_id": defect_id,
                "ambiente": rng.choice(ENVIRONMENTS),
                "release": rng.choice(RELEASES),
                "tester": rng.choice(TESTERS),
                "fecha_ejecucion": execution_date.isoformat(),
                "duracion_min": rng.randint(4, 75) if status != "No ejecutado" else 0,
                "evidencia": "Sí" if status in {"Aprobado", "Fallido", "Bloqueado"} and rng.random() > 0.08 else "No",
                "automatizado": "Sí" if rng.random() < 0.34 else "No",
            }
        )

    return records


def main() -> None:
    output = Path(__file__).parent / "data" / "casos_prueba_banco_ficticio.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    records = build_rows()
    with output.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
    print(f"Generados {len(records)} casos en {output}")


if __name__ == "__main__":
    main()
