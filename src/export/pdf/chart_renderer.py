"""
PDF Chart Renderer
High-resolution chart rendering for PDF reports

This module provides:
- Integration with existing chart_embedding.py system
- High-resolution PNG generation optimized for PDF embedding
- Chart sizing optimization for PDF layouts
- Batch chart processing for multiple visualizations
- Print-ready quality (300+ DPI) chart generation

Repository: https://github.com/LT-aitools/rent-vs-buy-decision-tool
"""

import asyncio
import logging
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

try:
    from ..excel.chart_embedding import ChartEmbedder
    CHART_EMBEDDER_AVAILABLE = True
except ImportError:
    CHART_EMBEDDER_AVAILABLE = False
    logging.warning("Chart embedder not available - PDF charts will be limited")

try:
    from PIL import Image as PILImage, ImageEnhance
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logging.warning("Pillow not available - image optimization will be limited")

logger = logging.getLogger(__name__)


class PDFChartRenderer:
    """
    Professional chart renderer for PDF reports
    
    Integrates with existing ChartEmbedder to provide optimized chart rendering
    specifically for PDF reports with high print quality and professional formatting.
    """
    
    def __init__(self, output_resolution: int = 300):
        """
        Initialize PDF chart renderer
        
        Args:
            output_resolution: Target resolution in DPI for PDF embedding (default 300 for print quality)
        """
        if not CHART_EMBEDDER_AVAILABLE:
            raise ImportError("Chart embedder is required for PDF chart rendering")
        
        self.resolution = output_resolution
        self.chart_embedder = ChartEmbedder()
        
        # PDF-optimized settings
        self.pdf_settings = {
            'format': 'png',
            'background_color': 'white',
            'transparent': False,
            'optimize_for_print': True,
            'enhance_contrast': True
        }
        
        logger.info(f"PDF Chart Renderer initialized at {self.resolution} DPI")
    
    async def render_all_charts_for_pdf(
        self,
        export_data: Dict[str, Any],
        output_dir: Optional[Path] = None,
        chart_types: Optional[List[str]] = None
    ) -> Dict[str, Path]:
        """
        Render all charts optimized for PDF embedding
        
        Args:
            export_data: Complete export data with analysis results
            output_dir: Directory for chart output (temp dir if None)
            chart_types: Specific chart types to render (all if None)
            
        Returns:
            Dictionary mapping chart names to optimized image paths
        """
        logger.info("Rendering charts optimized for PDF reports")
        
        # Set up output directory
        if output_dir is None:
            output_dir = Path(tempfile.mkdtemp()) / "pdf_charts"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Render base charts using existing system
        base_charts = await self.chart_embedder.render_all_charts(
            export_data=export_data,
            resolution=self.resolution,
            output_dir=output_dir
        )
        
        # Optimize charts for PDF
        pdf_optimized_charts = {}
        
        for chart_name, chart_path in base_charts.items():
            if chart_types is None or chart_name in chart_types:
                try:
                    optimized_path = await self._optimize_chart_for_pdf(
                        chart_path, output_dir, chart_name
                    )
                    pdf_optimized_charts[chart_name] = optimized_path
                    logger.debug(f"Optimized chart for PDF: {chart_name}")
                    
                except Exception as e:
                    logger.error(f"Error optimizing chart {chart_name}: {str(e)}")
                    # Fall back to original chart
                    pdf_optimized_charts[chart_name] = chart_path
        
        logger.info(f"Successfully optimized {len(pdf_optimized_charts)} charts for PDF")
        return pdf_optimized_charts
    
    async def _optimize_chart_for_pdf(
        self,
        chart_path: Path,
        output_dir: Path,
        chart_name: str
    ) -> Path:
        """
        Optimize individual chart for PDF embedding
        
        Args:
            chart_path: Path to original chart image
            output_dir: Output directory for optimized chart
            chart_name: Name identifier for the chart
            
        Returns:
            Path to PDF-optimized chart image
        """
        if not PIL_AVAILABLE:
            # Return original if PIL not available
            return chart_path
        
        optimized_path = output_dir / f"{chart_name}_pdf_optimized.png"
        
        try:
            with PILImage.open(chart_path) as img:
                # Convert to RGB if needed (removes transparency)
                if img.mode in ('RGBA', 'LA'):
                    # Create white background
                    background = PILImage.new('RGB', img.size, 'white')
                    if img.mode == 'RGBA':
                        background.paste(img, mask=img.split()[-1])  # Use alpha channel as mask
                    else:
                        background.paste(img, mask=img.split()[-1])
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Enhance for print quality
                if self.pdf_settings['enhance_contrast']:
                    # Slight contrast enhancement for print clarity
                    enhancer = ImageEnhance.Contrast(img)
                    img = enhancer.enhance(1.1)  # 10% contrast boost
                
                # Save with optimal settings for PDF
                img.save(
                    optimized_path,
                    'PNG',
                    dpi=(self.resolution, self.resolution),
                    optimize=True,
                    compress_level=6  # Good compression without quality loss
                )
                
                logger.debug(f"Chart optimized: {optimized_path}")
                
        except Exception as e:
            logger.error(f"Error optimizing chart {chart_name}: {str(e)}")
            # Copy original file as fallback
            import shutil
            shutil.copy2(chart_path, optimized_path)
        
        return optimized_path
    
    async def render_executive_summary_charts(
        self,
        export_data: Dict[str, Any],
        output_dir: Optional[Path] = None
    ) -> Dict[str, Path]:
        """
        Render charts specifically for executive summary
        
        Args:
            export_data: Export data
            output_dir: Output directory
            
        Returns:
            Dictionary of executive summary chart paths
        """
        executive_chart_types = [
            'npv_comparison',
            'financial_metrics'
        ]
        
        return await self.render_all_charts_for_pdf(
            export_data=export_data,
            output_dir=output_dir,
            chart_types=executive_chart_types
        )
    
    async def render_detailed_analysis_charts(
        self,
        export_data: Dict[str, Any],
        output_dir: Optional[Path] = None
    ) -> Dict[str, Path]:
        """
        Render all charts for detailed analysis report
        
        Args:
            export_data: Export data
            output_dir: Output directory
            
        Returns:
            Dictionary of all chart paths
        """
        return await self.render_all_charts_for_pdf(
            export_data=export_data,
            output_dir=output_dir
        )
    
    async def render_investor_presentation_charts(
        self,
        export_data: Dict[str, Any],
        output_dir: Optional[Path] = None
    ) -> Dict[str, Path]:
        """
        Render charts for investor presentation
        
        Args:
            export_data: Export data
            output_dir: Output directory
            
        Returns:
            Dictionary of investor-focused chart paths
        """
        investor_chart_types = [
            'npv_comparison',
            'annual_cash_flows',
            'sensitivity_analysis'
        ]
        
        return await self.render_all_charts_for_pdf(
            export_data=export_data,
            output_dir=output_dir,
            chart_types=investor_chart_types
        )
    
    async def create_custom_pdf_chart(
        self,
        chart_config: Dict[str, Any],
        export_data: Dict[str, Any],
        output_path: Optional[Path] = None
    ) -> Optional[Path]:
        """
        Create custom chart specifically for PDF requirements
        
        Args:
            chart_config: Configuration for custom chart
            export_data: Data for chart generation
            output_path: Output path for chart
            
        Returns:
            Path to generated chart or None if failed
        """
        logger.info(f"Creating custom PDF chart: {chart_config.get('type', 'unknown')}")
        
        try:
            # This method allows for future extension with custom chart types
            # that are specifically designed for PDF reports
            
            chart_type = chart_config.get('type')
            
            if chart_type == 'executive_metrics_dashboard':
                return await self._create_executive_metrics_dashboard(
                    export_data, chart_config, output_path
                )
            elif chart_type == 'investment_timeline':
                return await self._create_investment_timeline_chart(
                    export_data, chart_config, output_path
                )
            elif chart_type == 'risk_matrix':
                return await self._create_risk_matrix_chart(
                    export_data, chart_config, output_path
                )
            else:
                logger.warning(f"Unknown custom chart type: {chart_type}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating custom PDF chart: {str(e)}")
            return None
    
    async def _create_executive_metrics_dashboard(
        self,
        export_data: Dict[str, Any],
        config: Dict[str, Any],
        output_path: Optional[Path]
    ) -> Optional[Path]:
        """Create executive metrics dashboard chart (future implementation)"""
        
        # Placeholder for custom executive dashboard
        # This would create a comprehensive single-chart view
        # of all key metrics for executive presentation
        
        logger.info("Executive metrics dashboard chart not yet implemented")
        return None
    
    async def _create_investment_timeline_chart(
        self,
        export_data: Dict[str, Any],
        config: Dict[str, Any],
        output_path: Optional[Path]
    ) -> Optional[Path]:
        """Create investment timeline visualization (future implementation)"""
        
        # Placeholder for timeline chart showing key milestones,
        # cash flow events, and decision points over the analysis period
        
        logger.info("Investment timeline chart not yet implemented")
        return None
    
    async def _create_risk_matrix_chart(
        self,
        export_data: Dict[str, Any],
        config: Dict[str, Any],
        output_path: Optional[Path]
    ) -> Optional[Path]:
        """Create risk assessment matrix chart (future implementation)"""
        
        # Placeholder for risk matrix showing probability vs impact
        # of various risk factors
        
        logger.info("Risk matrix chart not yet implemented")
        return None
    
    def validate_chart_quality(self, chart_path: Path) -> Dict[str, Any]:
        """
        Validate chart quality for PDF embedding
        
        Args:
            chart_path: Path to chart image
            
        Returns:
            Dictionary with quality assessment
        """
        validation = {
            'exists': chart_path.exists(),
            'readable': False,
            'resolution_adequate': False,
            'format_correct': False,
            'file_size_reasonable': False
        }
        
        if not validation['exists']:
            return validation
        
        try:
            if PIL_AVAILABLE:
                with PILImage.open(chart_path) as img:
                    validation['readable'] = True
                    validation['format_correct'] = img.format == 'PNG'
                    
                    # Check resolution (should be at least 150 DPI equivalent)
                    width, height = img.size
                    min_width = int(6 * 150)  # 6 inches at 150 DPI minimum
                    validation['resolution_adequate'] = width >= min_width
                    
            # Check file size (should be reasonable but not too small)
            file_size = chart_path.stat().st_size
            validation['file_size_reasonable'] = 10000 < file_size < 5000000  # 10KB to 5MB
            
        except Exception as e:
            logger.error(f"Error validating chart quality: {str(e)}")
        
        validation['quality_score'] = sum(validation.values()) / len(validation)
        return validation
    
    def get_optimal_chart_dimensions_for_pdf(
        self,
        template_type: str = 'executive',
        chart_type: str = 'standard'
    ) -> Tuple[int, int]:
        """
        Get optimal chart dimensions for PDF embedding
        
        Args:
            template_type: PDF template type ('executive', 'detailed', 'investor')
            chart_type: Chart type for sizing optimization
            
        Returns:
            Tuple of (width_pixels, height_pixels)
        """
        # Base dimensions at target resolution
        base_width_inches = 7.0
        base_height_inches = 4.5
        
        # Adjust based on template type
        if template_type == 'executive':
            # Slightly larger for executive presentation
            width_inches = 7.5
            height_inches = 4.8
        elif template_type == 'investor':
            # Optimized for investor slides
            width_inches = 8.0
            height_inches = 5.0
        else:  # detailed
            # Standard size for detailed analysis
            width_inches = base_width_inches
            height_inches = base_height_inches
        
        # Adjust based on chart type
        if chart_type == 'metrics_comparison':
            # Wider for metric comparisons
            width_inches *= 1.2
            height_inches *= 0.9
        elif chart_type == 'cash_flow':
            # Standard aspect ratio for time series
            width_inches *= 1.1
        elif chart_type == 'sensitivity':
            # Optimized for tornado charts
            width_inches *= 1.0
            height_inches *= 0.8
        
        # Convert to pixels at target resolution
        width_pixels = int(width_inches * self.resolution)
        height_pixels = int(height_inches * self.resolution)
        
        return width_pixels, height_pixels
    
    def cleanup_temp_charts(self, chart_paths: Dict[str, Path]) -> None:
        """
        Clean up temporary chart files
        
        Args:
            chart_paths: Dictionary of chart paths to clean up
        """
        cleanup_count = 0
        
        for chart_name, chart_path in chart_paths.items():
            try:
                if chart_path.exists() and 'temp' in str(chart_path):
                    chart_path.unlink()
                    cleanup_count += 1
                    logger.debug(f"Cleaned up temp chart: {chart_name}")
            except Exception as e:
                logger.warning(f"Could not clean up chart {chart_name}: {str(e)}")
        
        if cleanup_count > 0:
            logger.info(f"Cleaned up {cleanup_count} temporary chart files")
    
    def get_chart_rendering_info(self) -> Dict[str, Any]:
        """
        Get information about chart rendering capabilities
        
        Returns:
            Dictionary with rendering capabilities and settings
        """
        return {
            'resolution': self.resolution,
            'settings': self.pdf_settings,
            'capabilities': {
                'chart_embedder_available': CHART_EMBEDDER_AVAILABLE,
                'pil_available': PIL_AVAILABLE,
                'supported_formats': ['png'],
                'optimization_features': [
                    'background_removal',
                    'contrast_enhancement',
                    'resolution_scaling',
                    'compression_optimization'
                ]
            },
            'chart_types': {
                'standard': [
                    'npv_comparison',
                    'annual_cash_flows',
                    'cumulative_cash_flows',
                    'financial_metrics',
                    'sensitivity_analysis'
                ],
                'custom': [
                    'executive_metrics_dashboard',
                    'investment_timeline',
                    'risk_matrix'
                ]
            },
            'quality_standards': {
                'min_resolution': f"{self.resolution} DPI",
                'format': 'PNG with RGB color space',
                'background': 'White (no transparency)',
                'compression': 'Optimized for PDF embedding'
            }
        }