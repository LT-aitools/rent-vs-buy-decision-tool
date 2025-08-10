"""
File Manager
Handles file operations for export system including temporary storage and cleanup

Manages the lifecycle of generated export files from creation through download,
ensuring proper cleanup and file organization.
"""

import logging
import shutil
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union


# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class ExportFile:
    """Represents a generated export file with metadata"""
    
    path: Path
    format: str  # "excel" or "pdf"
    template: str  # "executive", "detailed", "investor"
    size_mb: float
    generation_time: datetime
    download_count: int = 0
    expires_at: Optional[datetime] = None
    
    @property
    def filename(self) -> str:
        """Get the filename of the export file"""
        return self.path.name
    
    @property
    def exists(self) -> bool:
        """Check if the file still exists on disk"""
        return self.path.exists()
    
    @property
    def is_expired(self) -> bool:
        """Check if the file has expired"""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at


class FileManager:
    """
    Manages export file operations and lifecycle
    
    Handles temporary file storage, cleanup, and file organization
    for the export system.
    """
    
    def __init__(self, base_dir: Optional[Path] = None):
        """
        Initialize file manager
        
        Args:
            base_dir: Base directory for export file storage
        """
        self.base_dir = Path(base_dir) if base_dir else Path(tempfile.gettempdir()) / "real_estate_exports"
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # File tracking
        self.active_files: Dict[str, ExportFile] = {}
        
        logger.info(f"FileManager initialized with base_dir: {self.base_dir}")
    
    def register_file(self, export_file: ExportFile) -> str:
        """
        Register a new export file for tracking
        
        Args:
            export_file: ExportFile object to register
            
        Returns:
            File ID for tracking purposes
        """
        file_id = f"{export_file.format}_{export_file.template}_{export_file.generation_time.strftime('%Y%m%d_%H%M%S')}"
        self.active_files[file_id] = export_file
        
        logger.info(f"Registered export file: {file_id} ({export_file.size_mb:.2f} MB)")
        return file_id
    
    def get_file(self, file_id: str) -> Optional[ExportFile]:
        """
        Retrieve export file by ID
        
        Args:
            file_id: File identifier
            
        Returns:
            ExportFile if found, None otherwise
        """
        return self.active_files.get(file_id)
    
    def list_files(self, format_filter: Optional[str] = None) -> List[ExportFile]:
        """
        List all active export files
        
        Args:
            format_filter: Optional format filter ("excel" or "pdf")
            
        Returns:
            List of active export files
        """
        files = list(self.active_files.values())
        
        if format_filter:
            files = [f for f in files if f.format == format_filter]
        
        # Remove expired or missing files
        valid_files = []
        for export_file in files:
            if export_file.is_expired or not export_file.exists:
                self._remove_file_record(export_file)
            else:
                valid_files.append(export_file)
        
        return valid_files
    
    def mark_downloaded(self, file_id: str) -> bool:
        """
        Mark file as downloaded (increment download count)
        
        Args:
            file_id: File identifier
            
        Returns:
            True if successful, False if file not found
        """
        if file_id in self.active_files:
            self.active_files[file_id].download_count += 1
            logger.info(f"File {file_id} download count: {self.active_files[file_id].download_count}")
            return True
        return False
    
    def cleanup_file(self, file_id: str) -> bool:
        """
        Remove export file and clean up disk space
        
        Args:
            file_id: File identifier
            
        Returns:
            True if successful, False if file not found
        """
        if file_id not in self.active_files:
            return False
        
        export_file = self.active_files[file_id]
        
        # Remove physical file
        try:
            if export_file.path.exists():
                export_file.path.unlink()
                logger.info(f"Deleted file: {export_file.path}")
        except Exception as e:
            logger.warning(f"Failed to delete file {export_file.path}: {str(e)}")
        
        # Remove from tracking
        self._remove_file_record(export_file)
        return True
    
    def cleanup_expired_files(self) -> int:
        """
        Clean up all expired files
        
        Returns:
            Number of files cleaned up
        """
        expired_files = [
            file_id for file_id, export_file in self.active_files.items()
            if export_file.is_expired or not export_file.exists
        ]
        
        cleaned_count = 0
        for file_id in expired_files:
            if self.cleanup_file(file_id):
                cleaned_count += 1
        
        logger.info(f"Cleaned up {cleaned_count} expired files")
        return cleaned_count
    
    def cleanup_all_files(self) -> int:
        """
        Clean up all managed files
        
        Returns:
            Number of files cleaned up
        """
        file_ids = list(self.active_files.keys())
        cleaned_count = 0
        
        for file_id in file_ids:
            if self.cleanup_file(file_id):
                cleaned_count += 1
        
        logger.info(f"Cleaned up all {cleaned_count} files")
        return cleaned_count
    
    def get_storage_stats(self) -> Dict[str, Union[int, float]]:
        """
        Get storage statistics for managed files
        
        Returns:
            Dictionary with storage statistics
        """
        total_files = len(self.active_files)
        total_size_mb = sum(f.size_mb for f in self.active_files.values())
        excel_files = sum(1 for f in self.active_files.values() if f.format == "excel")
        pdf_files = sum(1 for f in self.active_files.values() if f.format == "pdf")
        
        return {
            'total_files': total_files,
            'total_size_mb': round(total_size_mb, 2),
            'excel_files': excel_files,
            'pdf_files': pdf_files,
            'avg_size_mb': round(total_size_mb / max(total_files, 1), 2)
        }
    
    def create_download_path(self, export_file: ExportFile) -> Path:
        """
        Create a user-friendly download path for the export file
        
        Args:
            export_file: Export file to create download path for
            
        Returns:
            Path suitable for download
        """
        # Create descriptive filename
        timestamp = export_file.generation_time.strftime('%Y%m%d_%H%M%S')
        filename = f"real_estate_analysis_{export_file.template}_{timestamp}.{export_file.format}"
        
        if export_file.format == "excel":
            filename = filename.replace(".excel", ".xlsx")
        elif export_file.format == "pdf":
            filename = filename.replace(".pdf", ".pdf")
        
        return export_file.path.parent / filename
    
    def _remove_file_record(self, export_file: ExportFile) -> None:
        """Remove file from tracking records"""
        # Find and remove file ID
        file_id_to_remove = None
        for file_id, tracked_file in self.active_files.items():
            if tracked_file.path == export_file.path:
                file_id_to_remove = file_id
                break
        
        if file_id_to_remove:
            del self.active_files[file_id_to_remove]
            logger.debug(f"Removed file record: {file_id_to_remove}")
    
    def __del__(self):
        """Cleanup on destruction"""
        try:
            # Don't automatically cleanup files - they may be needed for download
            pass
        except:
            pass