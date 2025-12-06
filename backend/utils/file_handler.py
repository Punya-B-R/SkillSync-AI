"""
File handling utilities for resume uploads.
"""
import os
from werkzeug.utils import secure_filename

class FileHandler:
    """Handle file uploads and storage."""
    
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    
    def __init__(self):
        # Create upload folder if it doesn't exist
        os.makedirs(self.UPLOAD_FOLDER, exist_ok=True)
    
    def allowed_file(self, filename):
        """
        Check if file extension is allowed.
        
        Args:
            filename: Name of the file
            
        Returns:
            bool: True if allowed, False otherwise
        """
        if not filename or '.' not in filename:
            return False
        file_ext = filename.rsplit('.', 1)[-1].lower()
        return file_ext in self.ALLOWED_EXTENSIONS
    
    def validate_file_size(self, file):
        """
        Validate file size.
        
        Args:
            file: File object from request
            
        Returns:
            bool: True if size is valid
            
        Raises:
            ValueError: If file size exceeds limit
        """
        file.seek(0, 2)  # Seek to end
        size = file.tell()
        file.seek(0)  # Reset to beginning
        
        if size > self.MAX_FILE_SIZE:
            raise ValueError(f"File size exceeds maximum allowed size (5MB)")
        
        if size == 0:
            raise ValueError("File is empty")
        
        return True
    
    def save_file(self, file):
        """
        Save uploaded file securely.
        
        Args:
            file: File object from request
            
        Returns:
            str: Path to saved file
        """
        # Validate file
        # Generate secure filename
        # Save file to UPLOAD_FOLDER
        # Return file path
        pass
    
    def get_file_type(self, filename):
        """
        Get file type from filename.
        
        Args:
            filename: Name of the file
            
        Returns:
            str: File type ('pdf', 'docx', or 'txt')
        """
        if not filename or '.' not in filename:
            return None
        return filename.rsplit('.', 1)[-1].lower()

