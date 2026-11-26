import pytest
from src.survey_runtime.clickhouse import ClickHouseCohortCompiler, QuerySpec

def test_compiler_generates_clickhouse_query_with_privacy_clause():
    compiler = ClickHouseCohortCompiler(table_name="employee_responses")
    spec = QuerySpec(
        survey_id="srv-engage-2026",
        dimensions=["department", "location"],
        metrics=["engagement", "leadership"],
        k_threshold=5,
        with_rollup=True
    )
    sql = compiler.compile(spec)

    assert "FROM employee_responses" in sql
    assert "survey_id = 'srv-engage-2026'" in sql
    assert "demographics['department'] AS department" in sql
    assert "HAVING count(*) >= 5" in sql
    assert "avg(scores['engagement'])" in sql
    assert "countIf(scores['engagement'] >= 4.0)" in sql
    assert "WITH ROLLUP" in sql

def test_compiler_validates_empty_dimensions():
    compiler = ClickHouseCohortCompiler()
    with pytest.raises(ValueError, match="at least one dimension"):
        compiler.compile(QuerySpec(survey_id="s1", dimensions=[], metrics=["m1"]))

def test_compiler_validates_empty_metrics():
    compiler = ClickHouseCohortCompiler()
    with pytest.raises(ValueError, match="at least one metric"):
        compiler.compile(QuerySpec(survey_id="s1", dimensions=["d1"], metrics=[]))
