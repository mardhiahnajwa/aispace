"""Chart generation utilities."""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64


class ChartGenerator:
    """Generate charts from data."""

    def __init__(self):
        sns.set_palette("husl")

    def _save_chart(self, fig):
        """Convert figure to base64."""
        buffer = BytesIO()
        fig.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode()
        plt.close(fig)
        return {
            "type": "chart",
            "format": "png",
            "data": f"data:image/png;base64,{image_base64}",
        }

    def bar_chart(self, df: pd.DataFrame, x: str, y: str, title: str = None):
        """Bar chart."""
        fig, ax = plt.subplots(figsize=(10, 6))
        df.plot(x=x, y=y, kind='bar', ax=ax)
        if title:
            ax.set_title(title, fontsize=14, fontweight='bold')
        plt.tight_layout()
        return self._save_chart(fig)

    def line_chart(self, df: pd.DataFrame, x: str, y: list, title: str = None):
        """Line chart."""
        fig, ax = plt.subplots(figsize=(10, 6))
        for col in y:
            ax.plot(df[x], df[col], marker='o', label=col)
        if title:
            ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend()
        plt.tight_layout()
        return self._save_chart(fig)

    def pie_chart(self, df: pd.DataFrame, values: str, labels: str, title: str = None):
        """Pie chart."""
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.pie(df[values], labels=df[labels], autopct='%1.1f%%')
        if title:
            ax.set_title(title, fontsize=14, fontweight='bold')
        plt.tight_layout()
        return self._save_chart(fig)

    def scatter_chart(self, df: pd.DataFrame, x: str, y: str, title: str = None):
        """Scatter chart."""
        fig, ax = plt.subplots(figsize=(10, 6))
        df.plot.scatter(x=x, y=y, ax=ax, s=100)
        if title:
            ax.set_title(title, fontsize=14, fontweight='bold')
        plt.tight_layout()
        return self._save_chart(fig)

    def histogram(self, df: pd.DataFrame, column: str, bins: int = 30, title: str = None):
        """Histogram."""
        fig, ax = plt.subplots(figsize=(10, 6))
        df[column].hist(bins=bins, ax=ax)
        if title:
            ax.set_title(title, fontsize=14, fontweight='bold')
        plt.tight_layout()
        return self._save_chart(fig)

    def heatmap(self, df: pd.DataFrame, title: str = None):
        """Heatmap."""
        fig, ax = plt.subplots(figsize=(12, 8))
        sns.heatmap(df, annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
        if title:
            ax.set_title(title, fontsize=14, fontweight='bold')
        plt.tight_layout()
        return self._save_chart(fig)


_generator_instance = None

def get_chart_gen() -> ChartGenerator:
    global _generator_instance
    if _generator_instance is None:
        _generator_instance = ChartGenerator()
    return _generator_instance
