"""Tools for the agent using @tool decorator."""
from langchain.tools import tool
import pandas as pd
import json
from .rag_system import get_rag
from .db_analyzer import get_analyzer
from .chart_gen import get_chart_gen


@tool
def retrieve_documents(query: str, k: int = 4) -> str:
    """Retrieve documents from knowledge base."""
    rag = get_rag()
    docs = rag.retrieve(query, k=k)
    result = {
        "count": len(docs),
        "documents": [
            {"content": doc.page_content[:300], "metadata": doc.metadata}
            for doc in docs
        ]
    }
    return json.dumps(result)


@tool
def search_database(table_name: str, search_term: str, limit: int = 10) -> str:
    """Search database table."""
    analyzer = get_analyzer()
    try:
        results = analyzer.quick_search(table_name, search_term, limit=limit)
        return json.dumps({"count": len(results), "results": results[:limit]})
    except Exception as e:
        return json.dumps({"error": str(e)})


@tool
def get_table_sample(table_name: str) -> str:
    """Get sample data from table."""
    analyzer = get_analyzer()
    try:
        df = analyzer.get_sample(table_name, limit=5)
        return json.dumps({
            "columns": df.columns.tolist(),
            "sample": df.to_dict(orient="records")
        })
    except Exception as e:
        return json.dumps({"error": str(e)})


@tool
def analyze_by_group(
    table_name: str,
    group_by: str,
    agg_column: str,
    agg_type: str = "SUM"
) -> str:
    """Aggregation analysis by grouping."""
    analyzer = get_analyzer()
    try:
        group_by_list = [x.strip() for x in group_by.split(",")]
        aggregations = {agg_column: agg_type}
        df = analyzer.analyze_aggregation(table_name, group_by_list, aggregations)
        return json.dumps({
            "data": df.to_dict(orient="records"),
            "rows": len(df)
        })
    except Exception as e:
        return json.dumps({"error": str(e)})


@tool
def analyze_trend(
    table_name: str,
    date_column: str,
    metric_column: str,
    interval: str = "month"
) -> str:
    """Trend analysis over time."""
    analyzer = get_analyzer()
    try:
        df = analyzer.analyze_trend(
            table_name, date_column, metric_column, interval
        )
        return json.dumps({
            "data": df.to_dict(orient="records"),
            "rows": len(df)
        })
    except Exception as e:
        return json.dumps({"error": str(e)})


@tool
def create_bar_chart(data: str, x_column: str, y_column: str, title: str = "Chart") -> str:
    """Create bar chart."""
    try:
        records = json.loads(data)
        df = pd.DataFrame(records)
        gen = get_chart_gen()
        chart = gen.bar_chart(df, x_column, y_column, title)
        return json.dumps({"status": "success", "chart_type": "bar"})
    except Exception as e:
        return json.dumps({"error": str(e)})


@tool
def create_line_chart(data: str, x_column: str, y_columns: str, title: str = "Chart") -> str:
    """Create line chart."""
    try:
        records = json.loads(data)
        df = pd.DataFrame(records)
        y_cols = [x.strip() for x in y_columns.split(",")]
        gen = get_chart_gen()
        chart = gen.line_chart(df, x_column, y_cols, title)
        return json.dumps({"status": "success", "chart_type": "line"})
    except Exception as e:
        return json.dumps({"error": str(e)})


@tool
def create_pie_chart(data: str, values_column: str, labels_column: str, title: str = "Chart") -> str:
    """Create pie chart."""
    try:
        records = json.loads(data)
        df = pd.DataFrame(records)
        gen = get_chart_gen()
        chart = gen.pie_chart(df, values_column, labels_column, title)
        return json.dumps({"status": "success", "chart_type": "pie"})
    except Exception as e:
        return json.dumps({"error": str(e)})


tools = [
    retrieve_documents,
    search_database,
    get_table_sample,
    analyze_by_group,
    analyze_trend,
    create_bar_chart,
    create_line_chart,
    create_pie_chart,
]
