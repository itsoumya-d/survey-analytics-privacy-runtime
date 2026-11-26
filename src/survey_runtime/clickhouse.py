from dataclasses import dataclass
from typing import List, Optional

@dataclass
class QuerySpec:
    survey_id: str
    dimensions: List[str]
    metrics: List[str]
    k_threshold: int = 5
    with_rollup: bool = True

class ClickHouseCohortCompiler:
    """Compiles demographic aggregation specifications into analytical ClickHouse queries with k-anonymity guarantees."""

    def __init__(self, table_name: str = "survey_responses_analytics"):
        self.table_name = table_name

    def compile(self, spec: QuerySpec) -> str:
        if not spec.dimensions:
            raise ValueError("QuerySpec must contain at least one dimension")
        if not spec.metrics:
            raise ValueError("QuerySpec must contain at least one metric")
        if spec.k_threshold < 1:
            raise ValueError("k_threshold must be >= 1")

        select_cols = []
        for dim in spec.dimensions:
            select_cols.append(f"demographics['{dim}'] AS {dim}")

        select_cols.append("count(*) AS respondent_count")

        for m in spec.metrics:
            select_cols.append(f"round(avg(scores['{m}']), 2) AS avg_{m}")
            select_cols.append(
                f"round((countIf(scores['{m}'] >= 4.0) / count(*)) * 100, 1) AS favorable_pct_{m}"
            )

        group_by = ", ".join(spec.dimensions)
        rollup_clause = " WITH ROLLUP" if spec.with_rollup else ""
        select_clause = ",\n    ".join(select_cols)

        sql = f"""SELECT
    {select_clause}
FROM {self.table_name}
WHERE survey_id = '{spec.survey_id}'
GROUP BY {group_by}{rollup_clause}
HAVING count(*) >= {spec.k_threshold}
ORDER BY respondent_count DESC"""
        return sql
