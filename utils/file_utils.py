import os
import pandas as pd
import time
import shutil
import logging

logger = logging.getLogger(__name__)

def allowed_file(filename, allowed_extensions):
    """Check if the file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def read_file_data(file_path, column_index, max_rows=None):
    """Read data from uploaded file based on file type"""
    file_ext = os.path.splitext(file_path)[1].lower()
    
    try:
        if file_ext in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)
        elif file_ext == '.csv':
            df = pd.read_csv(file_path)
        else:
            raise ValueError("Unsupported file format")
        
        # Adjust column index (0-based)
        if column_index >= len(df.columns):
            raise ValueError(f"Column index {column_index} out of range. File has {len(df.columns)} columns.")
        
        # Get data from specified column
        data = df.iloc[:, column_index].astype(str)
        
        # Filter out blank/NA values
        data = data[data.notna() & (data.str.strip() != '')]
        
        # Limit to max_rows if specified
        if max_rows and max_rows > 0:
            data = data.head(max_rows)
        
        return data.tolist()
    
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {str(e)}")
        raise

def cleanup_old_files(directory, max_age_seconds):
    """Remove old files and directories"""
    current_time = time.time()
    
    try:
        # Skip if directory doesn't exist
        if not os.path.exists(directory):
            return
        
        count_removed = 0
        
        # Check all subdirectories in the uploads folder
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            
            # Skip if not a directory
            if not os.path.isdir(item_path):
                continue
            
            # Check if the directory is older than max_age_seconds
            if current_time - os.path.getmtime(item_path) > max_age_seconds:
                shutil.rmtree(item_path, ignore_errors=True)
                count_removed += 1
        
        logger.info(f"Cleanup completed: removed {count_removed} old directories")
    
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")
