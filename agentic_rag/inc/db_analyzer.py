"""Database utilities for analysis."""
from typing import List, Dict, Any
from django.db import connections
import pandas as pd


class DatabaseAnalyzer:
    """Database querying and analysis."""

    def __init__(self, db_alias: str = "default"):
        self.connection = connections[db_alias]

    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """Execute raw SQL query."""
        with self.connection.cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description or []]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def get_dataframe(self, query: str) -> pd.DataFrame:
        """Execute query and return DataFrame."""
        with self.connection.cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description or []]
            rows = cursor.fetchall()
            return pd.DataFrame(rows, columns=columns)

    def quick_search(
        self,
        table_name: str,
        search_term: str,
        columns: List[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Quick search in table."""
        if not columns:
            columns = ["id", "name", "title", "content"]

        where_clause = " OR ".join(
            [f"`{col}` LIKE '%{search_term}%'" for col in columns]
        )
        query = f"SELECT * FROM `{table_name}` WHERE {where_clause} LIMIT {limit}"
        return self.execute_query(query)

    def get_sample(self, table_name: str, limit: int = 5) -> pd.DataFrame:
        """Get sample data."""
        query = f"SELECT * FROM `{table_name}` LIMIT {limit}"
        return self.get_dataframe(query)

    def analyze_aggregation(
        self,
        table_name: str,
        group_by: List[str],
        aggregations: Dict[str, str],
    ) -> pd.DataFrame:
        """Aggregation analysis."""
        agg_cols = ", ".join(
            [f"{func}({col}) as {col}_{func.lower()}"
             for col, func in aggregations.items()]
        )
        group_clause = ", ".join([f"`{col}`" for col in group_by])
        query = f"""
            SELECT {group_clause}, {agg_cols}
            FROM `{table_name}`
            GROUP BY {group_clause}
        """
        return self.get_dataframe(query)

    def analyze_trend(
        self,
        table_name: str,
        date_column: str,
        metric_column: str,
        interval: str = "day"
    ) -> pd.DataFrame:
        """Trend analysis."""
        date_format = {
            "day": "%Y-%m-%d",
            "week": "%Y-W%u",
            "month": "%Y-%m"
        }.get(interval, "%Y-%m-%d")

        query = f"""
            SELECT 
                DATE_FORMAT(`{date_column}`, '{date_format}') as period,
                COUNT(*) as count,
                AVG({metric_column}) as avg_value,
                SUM({metric_column}) as total_value
            FROM `{table_name}`
            GROUP BY period
            ORDER BY period DESC
        """
        return self.get_dataframe(query)


_analyzer_instance = None

def get_analyzer() -> DatabaseAnalyzer:
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = DatabaseAnalyzer()
    return _analyzer_instance
