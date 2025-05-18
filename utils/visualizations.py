import pandas as pd
import plotly.express as px
import streamlit as st
from langchain.tools import tool
from typing import Dict, Any, Optional
import json
from pydantic.v1 import BaseModel, Field
from datetime import datetime

class VisualizationGenerator:
    """Handles all data visualization operations with smart defaults and error recovery"""
    
    @staticmethod
    def auto_detect_chart_type(df: pd.DataFrame) -> str:
        """Determine the most appropriate chart type based on data characteristics"""
        numeric_cols = df.select_dtypes(include='number').columns.tolist()
        cat_cols = df.select_dtypes(exclude='number').columns.tolist()
        
        # Time series detection
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                return 'time_series'
                
        if not numeric_cols:
            return 'bar'  # Fallback for non-numeric data
            
        if len(numeric_cols) == 1 and len(cat_cols) >= 1:
            return 'pie' if len(df) <= 15 else 'bar'
            
        return 'histogram' if len(numeric_cols) >= 1 and not cat_cols else 'bar'

    @staticmethod
    def create_visualization(df: pd.DataFrame, chart_type: Optional[str] = None, **kwargs):
        """
        Unified visualization interface with auto-detection and smart defaults
        Args:
            df: Input DataFrame
            chart_type: Optional chart type override
            kwargs: Visualization parameters (x, y, names, values, etc.)
        """
        try:
            if df.empty:
                raise ValueError("Cannot visualize empty DataFrame")
                
            chart_type = chart_type or VisualizationGenerator.auto_detect_chart_type(df)
            df = VisualizationGenerator._preprocess_data(df, chart_type, kwargs)
            
            viz_methods = {
                'bar': VisualizationGenerator._create_bar,
                'pie': VisualizationGenerator._create_pie,
                'donut': VisualizationGenerator._create_donut,
                'histogram': VisualizationGenerator._create_histogram,
                'time_series': VisualizationGenerator._create_time_series
            }
            
            if chart_type not in viz_methods:
                raise ValueError(f"Unsupported chart type: {chart_type}")
                
            viz_methods[chart_type](df, **kwargs)
            
        except Exception as e:
            st.error(f"Visualization failed: {str(e)}")
            # Fallback to simple table display
            st.write("Displaying raw data instead:")
            st.dataframe(df)

    @staticmethod
    def _preprocess_data(df: pd.DataFrame, chart_type: str, kwargs: dict) -> pd.DataFrame:
        """Clean and prepare data for visualization"""
        # Handle datetime columns
        if chart_type == 'time_series':
            time_col = kwargs.get('x', next((col for col in df.columns if pd.api.types.is_datetime64_any_dtype(df[col])), None))
            if time_col:
                df[time_col] = pd.to_datetime(df[time_col])
                kwargs['x'] = time_col
        
        # Ensure numeric columns are properly typed
        for col in df.select_dtypes(include='object').columns:
            try:
                df[col] = pd.to_numeric(df[col])
            except (ValueError, TypeError):
                pass
                
        return df.copy()

    @staticmethod
    def _create_bar(df: pd.DataFrame, **kwargs):
        """Create bar chart with smart defaults"""
        x = kwargs.get('x', df.select_dtypes(exclude='number').columns[0] if not df.select_dtypes(exclude='number').empty else df.columns[0])
        y = kwargs.get('y', df.select_dtypes(include='number').columns[0] if not df.select_dtypes(include='number').empty else df.columns[1 % len(df.columns)])
        title = kwargs.get('title', f"{y} by {x}")
        
        fig = px.bar(df, x=x, y=y, title=title, 
                     color=x if len(df[x].unique()) <= 20 else None,
                     text_auto=True)
        st.plotly_chart(fig, use_container_width=True)

    @staticmethod
    def _create_pie(df: pd.DataFrame, **kwargs):
        """Create pie chart with parameter flexibility"""
        names = kwargs.get('names', kwargs.get('x', df.select_dtypes(exclude='number').columns[0]))
        values = kwargs.get('values', kwargs.get('y', df.select_dtypes(include='number').columns[0]))
        title = kwargs.get('title', f"Distribution of {values} by {names}")
        
        fig = px.pie(df, names=names, values=values, title=title,
                     hole=0, hover_data=[values])
        st.plotly_chart(fig, use_container_width=True)

    @staticmethod
    def _create_donut(df: pd.DataFrame, **kwargs):
        """Create donut chart with parameter flexibility"""
        names = kwargs.get('names', kwargs.get('x', df.select_dtypes(exclude='number').columns[0]))
        values = kwargs.get('values', kwargs.get('y', df.select_dtypes(include='number').columns[0]))
        title = kwargs.get('title', f"Distribution of {values} by {names}")
        
        fig = px.pie(df, names=names, values=values, title=title,
                     hole=0.4, hover_data=[values])
        st.plotly_chart(fig, use_container_width=True)

    @staticmethod
    def _create_histogram(df: pd.DataFrame, **kwargs):
        """Create histogram with smart binning"""
        column = kwargs.get('column', kwargs.get('x', df.select_dtypes(include='number').columns[0]))
        nbins = kwargs.get('nbins', min(50, len(df[column].unique())))
        title = kwargs.get('title', f"Distribution of {column}")
        
        fig = px.histogram(df, x=column, nbins=nbins, title=title,
                           marginal="box", hover_data=df.columns)
        st.plotly_chart(fig, use_container_width=True)

    @staticmethod
    def _create_time_series(df: pd.DataFrame, **kwargs):
        """Create time series plot with date handling"""
        x = kwargs.get('x', next((col for col in df.columns if pd.api.types.is_datetime64_any_dtype(df[col])), df.columns[0]))
        y = kwargs.get('y', df.select_dtypes(include='number').columns[0] if not df.select_dtypes(include='number').empty else df.columns[1 % len(df.columns)])
        title = kwargs.get('title', f"{y} over time")
        
        fig = px.line(df, x=x, y=y, title=title,
                      markers=True, line_shape="linear")
        fig.update_xaxes(rangeslider_visible=True)
        st.plotly_chart(fig, use_container_width=True)

def json_to_dataframe(json_data: Dict[str, Any]) -> pd.DataFrame:
    """Robust JSON to DataFrame conversion with multiple format support"""
    try:
        if isinstance(json_data, str):
            data = json.loads(json_data)
        else:
            data = json_data
            
        if isinstance(data, list):
            return pd.DataFrame(data)
            
        if 'data' in data and 'columns' in data:
            return pd.DataFrame(data['data'], columns=data['columns'])
            
        if 'values' in data and 'index' in data:  # For series-like data
            return pd.DataFrame(data['values'], index=data['index'])
            
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Data parsing error: {str(e)}")
        return pd.DataFrame()
    
class VizToolInput(BaseModel):
    chart_type: str = Field("auto", description="Type of chart to create")
    x: Optional[str] = Field(None, description="X-axis column")
    y: Optional[str] = Field(None, description="Y-axis column")
    names: Optional[str] = Field(None, description="Category names")
    values: Optional[str] = Field(None, description="Values column")
    title: Optional[str] = Field(None, description="Chart title")   

# Update the tool decorator
@tool(args_schema=VizToolInput)
def viz_tool(**kwargs) -> str:
    """
    Visualization tool that uses the current dataset from session state.
    Now only requires visualization parameters, not the full data payload.
    """
    try:
        if 'uploaded_df' not in st.session_state:
            return "No data available - upload a file first"
            
        df = st.session_state.uploaded_df
        VisualizationGenerator.create_visualization(df, **kwargs)
        return "Visualization rendered successfully"
    except Exception as e:
        return f"Visualization error: {str(e)}"