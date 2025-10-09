"""
Modern data handling utilities with standardized formats.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


class DataHandler:
    """Handle various input/output formats for geographic data."""
    
    REQUIRED_COLUMNS = ['longitude', 'latitude']
    LEGACY_MAPPING = {
        'start_long': 'longitude',
        'start_lat': 'latitude',
        'long': 'longitude', 
        'lat': 'latitude',
        'lng': 'longitude'
    }
    
    @classmethod
    def load_data(cls, data: str | Path | pd.DataFrame | np.ndarray | list) -> pd.DataFrame:
        """
        Load and standardize geographic data from various formats.
        
        Args:
            data: Input data in various formats
            
        Returns:
            Standardized DataFrame with longitude, latitude columns
        """
        if isinstance(data, (str, Path)):
            return cls._load_from_file(data)
        elif isinstance(data, pd.DataFrame):
            return cls._standardize_dataframe(data)
        elif isinstance(data, np.ndarray):
            return cls._from_numpy(data)
        elif isinstance(data, list):
            return cls._from_list(data)
        else:
            raise ValueError(f"Unsupported data type: {type(data)}")
    
    @classmethod
    def _load_from_file(cls, file_path: str | Path) -> pd.DataFrame:
        """Load data from file with automatic format detection."""
        file_path = Path(file_path)
        
        if file_path.suffix.lower() == '.csv':
            df = pd.read_csv(file_path)
        elif file_path.suffix.lower() == '.json':
            with open(file_path) as f:
                data = json.load(f)
            if 'features' in data:  # GeoJSON
                df = cls._from_geojson(data)
            else:
                df = pd.DataFrame(data)
        elif file_path.suffix.lower() in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)
        else:
            # Try CSV as fallback
            df = pd.read_csv(file_path)
            
        return cls._standardize_dataframe(df)
    
    @classmethod 
    def _standardize_dataframe(cls, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize DataFrame column names and format."""
        df = df.copy()
        
        # Map legacy column names
        for old_col, new_col in cls.LEGACY_MAPPING.items():
            if old_col in df.columns and new_col not in df.columns:
                df = df.rename(columns={old_col: new_col})
        
        # Check required columns exist
        missing_cols = [col for col in cls.REQUIRED_COLUMNS if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
            
        # Ensure numeric types
        for col in cls.REQUIRED_COLUMNS:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
        # Remove rows with NaN coordinates
        initial_len = len(df)
        df = df.dropna(subset=cls.REQUIRED_COLUMNS)
        if len(df) < initial_len:
            print(f"Warning: Removed {initial_len - len(df)} rows with invalid coordinates")
            
        return df
    
    @classmethod
    def _from_numpy(cls, data: np.ndarray) -> pd.DataFrame:
        """Convert numpy array to standardized DataFrame."""
        if data.ndim != 2 or data.shape[1] < 2:
            raise ValueError("NumPy array must be 2D with at least 2 columns [longitude, latitude]")
            
        df = pd.DataFrame(data[:, :2], columns=['longitude', 'latitude'])
        
        # Add additional columns if present
        if data.shape[1] > 2:
            for i in range(2, data.shape[1]):
                df[f'col_{i}'] = data[:, i]
                
        return df
    
    @classmethod
    def _from_list(cls, data: list) -> pd.DataFrame:
        """Convert list of coordinates to standardized DataFrame."""
        if not data:
            raise ValueError("Empty data list")
            
        # Handle list of tuples/lists
        if isinstance(data[0], (list, tuple)):
            return cls._from_numpy(np.array(data))
        
        # Handle list of dicts
        elif isinstance(data[0], dict):
            df = pd.DataFrame(data)
            return cls._standardize_dataframe(df)
        
        else:
            raise ValueError("List elements must be tuples, lists, or dictionaries")
    
    @classmethod
    def _from_geojson(cls, geojson: dict) -> pd.DataFrame:
        """Extract coordinates from GeoJSON format."""
        features = geojson.get('features', [])
        rows = []
        
        for feature in features:
            geometry = feature.get('geometry', {})
            properties = feature.get('properties', {})
            
            if geometry.get('type') == 'Point':
                coords = geometry.get('coordinates', [])
                if len(coords) >= 2:
                    row = {
                        'longitude': coords[0],
                        'latitude': coords[1]
                    }
                    row.update(properties)
                    rows.append(row)
                    
        if not rows:
            raise ValueError("No valid point features found in GeoJSON")
            
        return pd.DataFrame(rows)
    
    @staticmethod
    def save_results(result: Any, file_path: str | Path, format: str = 'auto') -> None:
        """
        Save results to file in specified format.
        
        Args:
            result: Result object to save
            file_path: Output file path
            format: Output format ('csv', 'json', 'auto')
        """
        file_path = Path(file_path)
        
        if format == 'auto':
            format = file_path.suffix.lower().lstrip('.')
            
        if hasattr(result, 'data') and isinstance(result.data, pd.DataFrame):
            data = result.data
        elif isinstance(result, pd.DataFrame):
            data = result
        else:
            raise ValueError("Cannot determine data to save from result")
            
        if format == 'csv':
            data.to_csv(file_path, index=False)
        elif format == 'json':
            data.to_json(file_path, orient='records', indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")