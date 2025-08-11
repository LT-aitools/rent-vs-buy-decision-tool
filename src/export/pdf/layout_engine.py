"""
PDF Layout Engine
Professional layout management for Real Estate Decision Tool PDF reports

This module provides:
- Page sizing, margins, and grid system management
- Text flow and section management
- Table layout and formatting utilities
- Chart positioning and sizing optimization
- Responsive layout for different content types

Repository: https://github.com/LT-aitools/rent-vs-buy-decision-tool
"""

import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum

try:
    from reportlab.lib.pagesizes import letter, A4, landscape
    from reportlab.lib.units import inch, mm, cm
    from reportlab.lib.colors import Color, HexColor
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
        Image, KeepTogether, Frame, PageTemplate
    )
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    logging.warning("ReportLab not available - layout engine will be limited")

logger = logging.getLogger(__name__)


class PageOrientation(Enum):
    """Page orientation options"""
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"


class ContentType(Enum):
    """Content type for layout optimization"""
    TEXT = "text"
    CHART = "chart"
    TABLE = "table"
    IMAGE = "image"
    METRICS = "metrics"
    HEADER = "header"


@dataclass
class LayoutDimensions:
    """Layout dimensions and spacing"""
    width: float
    height: float
    margin_top: float
    margin_bottom: float
    margin_left: float
    margin_right: float
    
    @property
    def content_width(self) -> float:
        """Available width for content"""
        return self.width - self.margin_left - self.margin_right
    
    @property
    def content_height(self) -> float:
        """Available height for content"""
        return self.height - self.margin_top - self.margin_bottom


@dataclass
class GridPosition:
    """Grid-based positioning system"""
    row: int
    col: int
    row_span: int = 1
    col_span: int = 1


class LayoutEngine:
    """
    Professional layout engine for PDF reports
    
    Provides comprehensive layout management including:
    - Grid-based positioning system
    - Responsive content sizing
    - Professional spacing and alignment
    - Chart and table optimization
    - Multi-column layouts
    """
    
    # Standard page sizes and margins
    PAGE_SIZES = {
        'letter': letter,
        'A4': A4,
        'letter_landscape': landscape(letter),
        'A4_landscape': landscape(A4)
    }
    
    # Standard margin sets
    MARGIN_PRESETS = {
        'standard': {'top': 1.0*inch, 'bottom': 1.0*inch, 'left': 0.75*inch, 'right': 0.75*inch},
        'narrow': {'top': 0.75*inch, 'bottom': 0.75*inch, 'left': 0.5*inch, 'right': 0.5*inch},
        'wide': {'top': 1.25*inch, 'bottom': 1.25*inch, 'left': 1.0*inch, 'right': 1.0*inch},
        'executive': {'top': 1.0*inch, 'bottom': 1.0*inch, 'left': 0.75*inch, 'right': 0.75*inch}
    }
    
    def __init__(self, page_size: str = 'letter', margin_preset: str = 'executive'):
        """
        Initialize layout engine
        
        Args:
            page_size: Page size identifier ('letter', 'A4', etc.)
            margin_preset: Margin preset identifier
        """
        if not REPORTLAB_AVAILABLE:
            raise ImportError("ReportLab is required for layout engine")
        
        self.page_size = self.PAGE_SIZES.get(page_size, letter)
        self.margins = self.MARGIN_PRESETS.get(margin_preset, self.MARGIN_PRESETS['executive'])
        
        # Calculate layout dimensions
        self.dimensions = LayoutDimensions(
            width=self.page_size[0],
            height=self.page_size[1],
            margin_top=self.margins['top'],
            margin_bottom=self.margins['bottom'],
            margin_left=self.margins['left'],
            margin_right=self.margins['right']
        )
        
        # Grid system (12-column grid)
        self.grid_columns = 12
        self.column_width = self.dimensions.content_width / self.grid_columns
        self.gutter_width = 0.1 * inch
        
        logger.info(f"Layout engine initialized: {page_size} page, {margin_preset} margins")
    
    def calculate_content_area(self, grid_start: int = 0, grid_span: int = 12) -> Tuple[float, float]:
        """
        Calculate content area dimensions based on grid position
        
        Args:
            grid_start: Starting grid column (0-11)
            grid_span: Number of columns to span (1-12)
            
        Returns:
            Tuple of (width, x_offset) for content area
        """
        if grid_start < 0 or grid_start >= self.grid_columns:
            raise ValueError(f"Grid start must be between 0 and {self.grid_columns-1}")
        
        if grid_span < 1 or grid_start + grid_span > self.grid_columns:
            raise ValueError(f"Invalid grid span: {grid_span} columns from position {grid_start}")
        
        # Calculate width including gutters
        width = (grid_span * self.column_width) - ((grid_span - 1) * self.gutter_width)
        x_offset = self.margins['left'] + (grid_start * (self.column_width + self.gutter_width))
        
        return width, x_offset
    
    def optimize_chart_size(
        self,
        content_type: ContentType = ContentType.CHART,
        grid_span: int = 12,
        aspect_ratio: float = 1.5  # width/height
    ) -> Tuple[float, float]:
        """
        Calculate optimal chart dimensions for given constraints
        
        Args:
            content_type: Type of content for sizing optimization
            grid_span: Number of grid columns to span
            aspect_ratio: Desired width/height ratio
            
        Returns:
            Tuple of (width, height) in points
        """
        content_width, _ = self.calculate_content_area(0, grid_span)
        
        if content_type == ContentType.CHART:
            # Charts should have good readability
            max_width = min(content_width, 7.5 * inch)  # Don't exceed 7.5 inches
            width = max_width
            height = width / aspect_ratio
            
            # Ensure height doesn't exceed reasonable limits
            max_height = 5 * inch
            if height > max_height:
                height = max_height
                width = height * aspect_ratio
                
        elif content_type == ContentType.METRICS:
            # Metric displays can be wider and shorter
            width = content_width * 0.8  # Leave some padding
            height = 2.5 * inch
            
        elif content_type == ContentType.TABLE:
            # Tables use full width available
            width = content_width
            height = None  # Let table determine height
            
        else:
            # Default sizing
            width = content_width * 0.9
            height = width / aspect_ratio
        
        return width, height
    
    def create_multi_column_layout(
        self,
        columns: int = 2,
        content_items: List[Any] = None
    ) -> List[Tuple[float, float, Any]]:
        """
        Create multi-column layout for content items
        
        Args:
            columns: Number of columns (2-4 supported)
            content_items: List of content items to layout
            
        Returns:
            List of (width, x_offset, content) tuples
        """
        if columns < 2 or columns > 4:
            raise ValueError("Multi-column layout supports 2-4 columns")
        
        if not content_items:
            content_items = []
        
        # Calculate column dimensions
        cols_per_column = self.grid_columns // columns
        layout_items = []
        
        for i, content in enumerate(content_items):
            col_index = i % columns
            grid_start = col_index * cols_per_column
            width, x_offset = self.calculate_content_area(grid_start, cols_per_column)
            layout_items.append((width, x_offset, content))
        
        return layout_items
    
    def create_table_style(
        self,
        style_type: str = 'professional',
        colors: Optional[Dict[str, Any]] = None
    ) -> TableStyle:
        """
        Create professional table styling
        
        Args:
            style_type: Style preset ('professional', 'executive', 'minimal')
            colors: Custom color scheme
            
        Returns:
            TableStyle object for ReportLab tables
        """
        if colors is None:
            if REPORTLAB_AVAILABLE:
                colors = {
                    'header_bg': HexColor('#FF6B6B'),
                    'header_text': HexColor('#FFFFFF'),
                    'row_bg': HexColor('#F8F9FA'),
                    'text': HexColor('#2D3436'),
                    'border': HexColor('#E9ECEF')
                }
            else:
                colors = {}
        
        if not REPORTLAB_AVAILABLE:
            return None
            
        if style_type == 'professional':
            table_style = TableStyle([
                # Header styling
                ('BACKGROUND', (0, 0), (-1, 0), colors['header_bg']),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors['header_text']),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 0), (-1, 0), 12),
                
                # Body styling
                ('BACKGROUND', (0, 1), (-1, -1), colors['row_bg']),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors['text']),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                ('TOPPADDING', (0, 1), (-1, -1), 8),
                
                # Alignment and borders
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 1, colors['border']),
                
                # Alternating row colors for readability
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors['row_bg'], colors.get('white', colors['row_bg'])])
            ])
            
        elif style_type == 'executive':
            table_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors['header_bg']),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors['header_text']),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 15),
                ('TOPPADDING', (0, 0), (-1, 0), 15),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 10),
                ('TOPPADDING', (0, 1), (-1, -1), 10),
                ('LINEBELOW', (0, 0), (-1, 0), 2, colors['header_bg']),
                ('LINEAFTER', (0, 0), (-1, -1), 1, colors['border'])
            ])
            
        else:  # minimal
            table_style = TableStyle([
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('LINEBELOW', (0, 0), (-1, 0), 1, colors['border'])
            ])
        
        return table_style
    
    def calculate_table_column_widths(
        self,
        num_columns: int,
        total_width: Optional[float] = None,
        column_ratios: Optional[List[float]] = None
    ) -> List[float]:
        """
        Calculate optimal column widths for tables
        
        Args:
            num_columns: Number of table columns
            total_width: Total available width (uses content width if None)
            column_ratios: Relative width ratios for columns
            
        Returns:
            List of column widths in points
        """
        if total_width is None:
            total_width = self.dimensions.content_width
        
        if column_ratios is None:
            # Equal width columns
            column_width = total_width / num_columns
            return [column_width] * num_columns
        
        if len(column_ratios) != num_columns:
            raise ValueError("Column ratios must match number of columns")
        
        # Normalize ratios and calculate widths
        total_ratio = sum(column_ratios)
        normalized_ratios = [ratio / total_ratio for ratio in column_ratios]
        
        return [total_width * ratio for ratio in normalized_ratios]
    
    def create_metric_card_layout(
        self,
        metrics: List[Dict[str, Any]],
        cards_per_row: int = 3
    ) -> List[List[Dict[str, Any]]]:
        """
        Create layout for metric cards in rows
        
        Args:
            metrics: List of metric dictionaries with 'label', 'value', 'format'
            cards_per_row: Number of cards per row
            
        Returns:
            List of rows, each containing metric card layouts
        """
        rows = []
        current_row = []
        
        for i, metric in enumerate(metrics):
            current_row.append(metric)
            
            if len(current_row) == cards_per_row or i == len(metrics) - 1:
                rows.append(current_row)
                current_row = []
        
        # Calculate dimensions for each card
        card_width = self.dimensions.content_width / cards_per_row - (0.1 * inch)
        
        for row in rows:
            for card in row:
                card['width'] = card_width
                card['height'] = 1.5 * inch
        
        return rows
    
    def create_section_spacing(self, section_type: str = 'normal') -> Spacer:
        """
        Create appropriate spacing for different section types
        
        Args:
            section_type: Type of section ('title', 'heading', 'normal', 'chart', 'table')
            
        Returns:
            Spacer object with appropriate height
        """
        spacing_map = {
            'title': 0.5 * inch,
            'heading': 0.3 * inch,
            'normal': 0.2 * inch,
            'chart': 0.25 * inch,
            'table': 0.2 * inch,
            'small': 0.1 * inch
        }
        
        height = spacing_map.get(section_type, spacing_map['normal'])
        return Spacer(1, height)
    
    def optimize_image_for_layout(
        self,
        image_path: str,
        target_width: Optional[float] = None,
        max_height: Optional[float] = None,
        maintain_aspect: bool = True
    ) -> Tuple[float, float]:
        """
        Calculate optimal image dimensions for layout
        
        Args:
            image_path: Path to image file
            target_width: Target width in points
            max_height: Maximum height in points
            maintain_aspect: Whether to maintain aspect ratio
            
        Returns:
            Tuple of (width, height) in points
        """
        try:
            from PIL import Image as PILImage
            
            with PILImage.open(image_path) as img:
                original_width, original_height = img.size
                aspect_ratio = original_width / original_height
        except Exception:
            # Fallback to default chart dimensions
            aspect_ratio = 1.5
            original_width, original_height = 600, 400
        
        if target_width is None:
            target_width = self.dimensions.content_width * 0.8
        
        if maintain_aspect:
            height = target_width / aspect_ratio
            
            if max_height and height > max_height:
                height = max_height
                target_width = height * aspect_ratio
        else:
            height = max_height or (4 * inch)
        
        return target_width, height
    
    def get_layout_info(self) -> Dict[str, Any]:
        """
        Get comprehensive layout information
        
        Returns:
            Dictionary with layout dimensions and capabilities
        """
        return {
            'page_size': self.page_size,
            'margins': self.margins,
            'dimensions': {
                'page_width': self.dimensions.width,
                'page_height': self.dimensions.height,
                'content_width': self.dimensions.content_width,
                'content_height': self.dimensions.content_height
            },
            'grid': {
                'columns': self.grid_columns,
                'column_width': self.column_width,
                'gutter_width': self.gutter_width
            },
            'capabilities': {
                'multi_column': True,
                'responsive_sizing': True,
                'chart_optimization': True,
                'table_styling': True,
                'metric_cards': True
            }
        }