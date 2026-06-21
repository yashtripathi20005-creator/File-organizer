"""
File Organizer - File Operations Module
Contains core file organization and renaming logic
"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Dict


class FileOrganizer:
    """Core file organization and renaming class"""
    
    def __init__(self):
        self.files_processed = 0
        self.errors = []
    
    def get_files(self, folder_path: str) -> List[str]:
        """Get list of files in the folder"""
        if not os.path.exists(folder_path):
            raise ValueError(f"Folder does not exist: {folder_path}")
        
        files = []
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            if os.path.isfile(item_path) and not item.startswith('.'):
                files.append(item)
        return sorted(files)
    
    def generate_new_name(self, 
                         old_name: str,
                         pattern_type: str,
                         prefix: str = "",
                         suffix: str = "",
                         use_date: bool = False,
                         date_format: str = "%Y%m%d",
                         start_number: int = 1,
                         use_extension: bool = True) -> str:
        """
        Generate a new filename based on the specified pattern
        
        Args:
            old_name: Original filename
            pattern_type: Type of naming pattern
            prefix: Prefix to add
            suffix: Suffix to add
            use_date: Whether to include date
            date_format: Format for the date
            start_number: Starting number for counting
            use_extension: Whether to keep original extension
        
        Returns:
            New filename
        """
        # Split name and extension
        if use_extension:
            name_parts = os.path.splitext(old_name)
            name = name_parts[0]
            ext = name_parts[1]
        else:
            name = old_name
            ext = ""
        
        # Generate date string if needed
        date_str = ""
        if use_date:
            now = datetime.now()
            date_str = now.strftime(date_format)
        
        # Generate number string
        number_str = str(start_number).zfill(3) if start_number < 1000 else str(start_number)
        
        # Build new name based on pattern
        pattern_lower = pattern_type.lower()
        
        # Different pattern types
        if "custom" in pattern_lower and "number" in pattern_lower:
            # Custom + Number
            if prefix or suffix:
                new_name = prefix + number_str + suffix
            else:
                new_name = "file" + number_str
                
        elif "custom" in pattern_lower and "date" in pattern_lower:
            # Custom + Date
            if prefix or suffix:
                new_name = prefix + date_str + suffix
            else:
                new_name = "file_" + date_str
                
        elif "prefix only" in pattern_lower:
            new_name = prefix if prefix else "file"
            
        elif "suffix only" in pattern_lower:
            new_name = suffix if suffix else "file"
            
        elif "date only" in pattern_lower:
            new_name = date_str if date_str else "file"
            
        elif "number only" in pattern_lower:
            new_name = number_str
            
        elif "prefix + number" in pattern_lower:
            prefix_text = prefix if prefix else "file"
            new_name = f"{prefix_text}{number_str}"
            
        elif "prefix + date" in pattern_lower:
            prefix_text = prefix if prefix else "file"
            new_name = f"{prefix_text}_{date_str}" if date_str else prefix_text
            
        elif "number + suffix" in pattern_lower:
            suffix_text = suffix if suffix else "file"
            new_name = f"{number_str}_{suffix_text}"
            
        elif "date + suffix" in pattern_lower:
            suffix_text = suffix if suffix else "file"
            new_name = f"{date_str}_{suffix_text}" if date_str else suffix_text
            
        elif "custom pattern" in pattern_lower:
            # Build custom pattern from prefix and suffix
            parts = []
            if prefix:
                parts.append(prefix)
            if use_date and date_str:
                parts.append(date_str)
            if suffix:
                parts.append(suffix)
            new_name = "_".join(parts) if parts else "file"
            
        else:
            # Default: Use prefix if available
            new_name = prefix if prefix else "file"
        
        # Clean up the name (remove special characters, spaces, etc.)
        new_name = self.sanitize_filename(new_name)
        
        # Add extension back
        if use_extension and ext:
            return new_name + ext
        else:
            return new_name
    
    def sanitize_filename(self, filename: str) -> str:
        """Remove illegal characters from filename"""
        # Replace spaces with underscores
        filename = filename.replace(' ', '_')
        # Remove characters that are illegal in filenames
        illegal_chars = r'[<>:"/\\|?*]'
        filename = re.sub(illegal_chars, '', filename)
        # Remove multiple underscores
        filename = re.sub(r'_+', '_', filename)
        # Remove leading/trailing underscores and dots
        filename = filename.strip('_ .')
        return filename
    
    def preview_rename(self,
                      folder_path: str,
                      pattern_type: str,
                      prefix: str = "",
                      suffix: str = "",
                      use_date: bool = False,
                      date_format: str = "%Y%m%d",
                      start_number: int = 1,
                      use_extension: bool = True) -> List[Tuple[str, str]]:
        """
        Preview the renaming operation without actually renaming files
        
        Returns:
            List of tuples (old_name, new_name)
        """
        files = self.get_files(folder_path)
        preview_list = []
        counter = start_number
        
        for file in files:
            # Generate new name with current counter
            new_name = self.generate_new_name(
                old_name=file,
                pattern_type=pattern_type,
                prefix=prefix,
                suffix=suffix,
                use_date=use_date,
                date_format=date_format,
                start_number=counter,
                use_extension=use_extension
            )
            
            # Ensure uniqueness
            new_name = self.ensure_unique_name(new_name, [name for _, name in preview_list])
            
            preview_list.append((file, new_name))
            counter += 1
        
        return preview_list
    
    def ensure_unique_name(self, filename: str, existing_names: List[str]) -> str:
        """Ensure filename is unique"""
        if filename not in existing_names:
            return filename
        
        # If filename exists, add a number
        name_parts = os.path.splitext(filename)
        base_name = name_parts[0]
        ext = name_parts[1] if len(name_parts) > 1 else ""
        
        counter = 1
        while True:
            new_name = f"{base_name}_{counter}{ext}"
            if new_name not in existing_names:
                return new_name
            counter += 1
    
    def organize_files(self,
                      folder_path: str,
                      pattern_type: str,
                      prefix: str = "",
                      suffix: str = "",
                      use_date: bool = False,
                      date_format: str = "%Y%m%d",
                      start_number: int = 1,
                      use_extension: bool = True,
                      dry_run: bool = False) -> Dict:
        """
        Organize files by renaming them according to the specified pattern
        
        Returns:
            Dict containing success status, renamed count, and error messages
        """
        result = {
            'success': False,
            'renamed': 0,
            'errors': [],
            'error': ''
        }
        
        try:
            files = self.get_files(folder_path)
            if not files:
                result['error'] = "No files found in the folder"
                return result
            
            preview_list = self.preview_rename(
                folder_path=folder_path,
                pattern_type=pattern_type,
                prefix=prefix,
                suffix=suffix,
                use_date=use_date,
                date_format=date_format,
                start_number=start_number,
                use_extension=use_extension
            )
            
            if dry_run:
                result['success'] = True
                result['renamed'] = len(preview_list)
                return result
            
            renamed_count = 0
            errors = []
            
            for old_name, new_name in preview_list:
                if old_name == new_name:
                    continue  # No change needed
                
                old_path = os.path.join(folder_path, old_name)
                new_path = os.path.join(folder_path, new_name)
                
                try:
                    os.rename(old_path, new_path)
                    renamed_count += 1
                except Exception as e:
                    errors.append(f"Failed to rename '{old_name}': {str(e)}")
            
            result['success'] = True
            result['renamed'] = renamed_count
            result['errors'] = errors
            
            if errors:
                result['error'] = f"Completed with {len(errors)} errors"
            
        except Exception as e:
            result['error'] = str(e)
            result['success'] = False
        
        return result
