from __future__ import annotations

import json
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(slots=True)
class StrategyRecommendation:
    strategy_name: str
    avg_performance: float
    usage_count: int
    avg_iterations: float
    avg_time: float


class LocalStrategyMemory:
    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self._db_path)

    def _initialize(self) -> None:
        with self._connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS optimization_runs (
                    id TEXT PRIMARY KEY,
                    domain TEXT NOT NULL,
                    strategy TEXT NOT NULL,
                    features_json TEXT NOT NULL,
                    final_value REAL,
                    iterations INTEGER,
                    solve_time REAL,
                    success INTEGER NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_runs_domain ON optimization_runs(domain)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_runs_domain_strategy ON optimization_runs(domain, strategy)"
            )

    def store_optimization_result(
        self,
        strategy_name: str,
        domain: str,
        problem_features: dict[str, object],
        performance_metrics: dict[str, object],
    ) -> bool:
        final_value = _as_float(performance_metrics.get("final_value", 0.0))
        iterations = _as_int(performance_metrics.get("iterations", 0))
        solve_time = _as_float(performance_metrics.get("time", 0.0))
        success = bool(performance_metrics.get("success", False))

        with self._connection() as conn:
            conn.execute(
                """
                INSERT INTO optimization_runs (
                    id, domain, strategy, features_json, final_value, iterations,
                    solve_time, success, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(uuid.uuid4()),
                    domain,
                    strategy_name,
                    json.dumps(problem_features),
                    final_value,
                    iterations,
                    solve_time,
                    1 if success else 0,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
        return True

    def get_strategy_recommendations(
        self,
        domain: str,
        limit: int = 3,
        *,
        descriptor_mix: str | None = None,
    ) -> list[StrategyRecommendation]:
        """Rank strategies by average final_value for a domain.

        When ``descriptor_mix`` is set (e.g. ``\"mixed\"``, ``\"discrete_only\"``), only rows whose
        ``features_json`` contains that ``descriptor_mix`` value are aggregated. If that yields no
        rows, falls back to domain-only aggregation.
        """
        base_sql = """
                SELECT
                    strategy,
                    AVG(final_value) AS avg_performance,
                    COUNT(*) AS usage_count,
                    AVG(iterations) AS avg_iterations,
                    AVG(solve_time) AS avg_time
                FROM optimization_runs
                WHERE domain = ?
                """
        group_sql = """
                GROUP BY strategy
                HAVING usage_count >= 1
                ORDER BY avg_performance ASC, usage_count DESC
                LIMIT ?
                """

        with self._connection() as conn:
            if descriptor_mix is None:
                rows = conn.execute(
                    base_sql + group_sql,
                    (domain, limit),
                ).fetchall()
            else:
                filtered = (
                    base_sql
                    + " AND json_extract(features_json, '$.descriptor_mix') = ? "
                    + group_sql
                )
                rows = conn.execute(
                    filtered,
                    (domain, descriptor_mix, limit),
                ).fetchall()
                if not rows:
                    rows = conn.execute(
                        base_sql + group_sql,
                        (domain, limit),
                    ).fetchall()

        return [
            StrategyRecommendation(
                strategy_name=row[0],
                avg_performance=float(row[1] if row[1] is not None else 0.0),
                usage_count=int(row[2]),
                avg_iterations=float(row[3] if row[3] is not None else 0.0),
                avg_time=float(row[4] if row[4] is not None else 0.0),
            )
            for row in rows
        ]


def _as_float(value: object) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        return float(value)
    return 0.0


def _as_int(value: object) -> int:
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        return int(value)
    return 0
