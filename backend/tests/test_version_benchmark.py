from app.services.version_benchmark import get_version_benchmark


def test_version_benchmark_is_metric_based_for_v4():
    benchmark = get_version_benchmark()

    assert benchmark["baseline"] == "v1"
    assert benchmark["comparison"] == "v1 vs v2 vs v3 vs v4"
    assert benchmark["candidate"].startswith("v4")
    assert benchmark["current_version"] == "v4"
    assert benchmark["summary"]["metric_count"] >= 15
    assert benchmark["summary"]["regressions"] == 0
    assert benchmark["summary"]["improved"] > benchmark["summary"]["unchanged"]


def test_version_benchmark_has_expected_core_metrics():
    benchmark = get_version_benchmark()
    metrics = {item["metric"]: item for item in benchmark["metrics"]}

    assert metrics["Automated regression tests"]["v1"] == 9
    assert metrics["Automated regression tests"]["v2"] == 20
    assert metrics["Automated regression tests"]["v3"] == 25
    assert metrics["Automated regression tests"]["v4"] == 35
    assert metrics["RAG provenance metadata"]["v2"] > metrics["RAG provenance metadata"]["v1"]
    assert metrics["Korean intent coverage"]["v3"] > metrics["Korean intent coverage"]["v2"]
    assert metrics["Korean intent coverage"]["v4"] > metrics["Korean intent coverage"]["v3"]
    assert metrics["Prompt quality artifacts"]["v4"] == 14
    assert metrics["Research source coverage"]["v3"] == 4
    assert metrics["Research persona modes"]["v3"] == 3
    assert metrics["Persona/manner eval criteria"]["v3"] == 3
    assert metrics["Model routing policies"]["v4"] == 4
    assert metrics["Bounded fandom safety labels"]["v4"] == 8
