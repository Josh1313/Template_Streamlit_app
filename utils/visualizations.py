import pandas as pd
import plotly.express as px
import streamlit as st
from langchain.tools import tool
from typing import Dict, Any, Optional
import json
from pydantic.v1 import BaseModel, Field
import warnings

class VisualizationGenerator:
    """Enhanced visualization handler with schema-aligned parameters"""
    
    @staticmethod
    def auto_detect_chart_type(df: pd.DataFrame) -> str:
        """Simplified chart type detection for supported types"""
        numeric_cols = df.select_dtypes(include='number').columns
        categorical_cols = df.select_dtypes(exclude='number').columns

        if len(numeric_cols) == 1 and len(categorical_cols) >= 1:
            return 'pie' if len(df) <= 15 else 'bar'
        if len(numeric_cols) >= 1 and len(categorical_cols) >= 1:
            return 'bar'
        return 'bar'  # Default fallback

    @staticmethod
    def create_visualization(
        df: pd.DataFrame,
        chart_type: Optional[str] = None,
        **kwargs
    ) -> None:
        """Controller for rendering charts in Streamlit"""
        try:
            if df.empty:
                raise ValueError("Empty DataFrame received")

            # Determine chart type
            ct = (chart_type or
                  VisualizationGenerator.auto_detect_chart_type(df))
            # Preprocess dates
            df_proc = VisualizationGenerator._preprocess_data(df.copy())

            # Validate required columns
            VisualizationGenerator._validate_columns(ct, df_proc, kwargs)

            # Dispatch to renderer
            if ct == 'bar':
                VisualizationGenerator._create_bar(df_proc, **kwargs)
            elif ct == 'pie':
                VisualizationGenerator._create_pie(df_proc, **kwargs)
            else:
                raise ValueError(f"Unsupported chart type: {ct}")

        except Exception as e:
            st.error(f"Visualization error: {e}")
            st.dataframe(df.head(3))

    @staticmethod
    def _preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
        """Attempt silent datetime conversion"""
        for col in df.columns:
            if pd.api.types.is_string_dtype(df[col]):
                with warnings.catch_warnings():
                    warnings.filterwarnings('ignore', category=UserWarning)
                df[col] = pd.to_datetime(df[col], errors='ignore', infer_datetime_format=True)
        return df

    @staticmethod
    def _validate_columns(
        chart_type: str,
        df: pd.DataFrame,
        params: Dict[str, Any]
    ) -> None:
        """Ensure required fields are present based on chart type"""
        missing = []
        if chart_type == 'bar':
            x = params.get('x_axis')
            y = params.get('y_axis')
            if not x:
                raise ValueError("Parameter 'x_axis' is required for bar charts.")
            if not y:
                raise ValueError("Parameter 'y_axis' is required for bar charts.")
            missing = [c for c in (x, y) if c not in df.columns]
        elif chart_type == 'pie':
            labels = params.get('labels')
            values = params.get('values')
            if not labels:
                raise ValueError("Parameter 'labels' is required for pie charts.")
            if not values:
                raise ValueError("Parameter 'values' is required for pie charts.")
            missing = [c for c in (labels, values) if c not in df.columns]

        if missing:
            raise ValueError(f"Missing required columns: {', '.join(missing)}")

    @staticmethod
    def _create_bar(df: pd.DataFrame, **params) -> None:
        x = params.get('x_axis')
        y = params.get('y_axis')
        title = params.get('title', f"{y} by {x}")

        # If y == 'count', aggregate counts
        if str(y).lower() == 'count':
            df_agg = df.groupby(x).size().reset_index(name='Count')
            y_col = 'Count'
        else:
            df_agg = df
            y_col = y

        fig = px.bar(
            df_agg,
            x=x,
            y=y_col,
            title=title,
            text_auto=True
        )
        st.plotly_chart(fig, use_container_width=True)

    @staticmethod
    def _create_pie(df: pd.DataFrame, **params) -> None:
        labels = params.get('labels')
        values = params.get('values')
        title = params.get('title', f"Distribution of {values}")

        fig = px.pie(
            df,
            names=labels,
            values=values,
            title=title,
            hole=0.3
        )
        st.plotly_chart(fig, use_container_width=True)


def json_to_dataframe(json_data: Dict[str, Any]) -> pd.DataFrame:
    """Convert JSON payload to DataFrame"""
    try:
        if isinstance(json_data, str):
            data = json.loads(json_data)
        else:
            data = json_data

        if isinstance(data, dict) and 'data' in data and 'columns' in data:
            return pd.DataFrame(data['data'], columns=data['columns'])
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Data parsing failed: {e}")
        return pd.DataFrame()

class VizToolInput(BaseModel):
    """Input schema for visualization tool"""
    chart_type: str = Field(..., description="Chart type: bar|pie")
    x_axis: Optional[str] = Field(None, description="X-axis column (bar)")
    y_axis: Optional[str] = Field(None, description="Y-axis column (bar)")
    labels: Optional[str] = Field(None, description="Category labels (pie)")
    values: Optional[str] = Field(None, description="Values column (pie)")
    title: Optional[str] = Field(None, description="Chart title")

@tool(args_schema=VizToolInput)
def viz_tool(**kwargs) -> str:
    """LangChain function for rendering charts"""
    try:
        if 'uploaded_df' not in st.session_state:
            return "Error: No data uploaded."
        df = st.session_state.uploaded_df
        if df.empty:
            return "Error: Empty dataset."

        # Render
        VisualizationGenerator.create_visualization(df, **kwargs)
        return "Visualization rendered successfully."
    except Exception as e:
        return f"Visualization failed: {e}."
