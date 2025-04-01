import os
import shutil
import subprocess
import sys
from pathlib import Path

def find_upscaler_file(upscaler_name):
    """Find an upscaler file by name in various locations"""
    # Check in standard locations
    search_paths = [
        os.path.join(os.path.dirname(__file__), 'models/upscalers'),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models/upscalers'),
        os.path.join(os.path.dirname(__file__), 'models'),
        '/workspace/models/upscalers',
        '/workspace'
    ]
    
    # Look for the file in each search path
    for path in search_paths:
        if os.path.exists(path):
            potential_path = os.path.join(path, upscaler_name)
            if os.path.exists(potential_path):
                return potential_path
    
    # If not found, search more broadly
    for path in search_paths:
        if os.path.exists(path):
            for root, dirs, files in os.walk(path):
                if upscaler_name in files:
                    return os.path.join(root, upscaler_name)
    
    # Last resort - search the entire file system (with limits)
    try:
        print(f"Searching for {upscaler_name} in the file system...")
        result = subprocess.run(
            ["find", "/", "-name", upscaler_name, "-type", "f", "-not", "-path", "*/\\.*"],
            capture_output=True, text=True, timeout=30
        )
        if result.stdout:
            found_path = result.stdout.strip().split('\n')[0]
            if os.path.exists(found_path):
                return found_path
    except Exception as e:
        print(f"Error searching for upscaler: {e}")
    
    return None

def ensure_upscaler_directory():
    """Ensure the upscaler directory exists"""
    upscaler_dir = os.path.join(os.path.dirname(__file__), 'models/upscalers')
    os.makedirs(upscaler_dir, exist_ok=True)
    return upscaler_dir

def copy_upscaler_to_standard_location(src_path, upscaler_name=None):
    """Copy an upscaler file to the standard location"""
    if upscaler_name is None:
        upscaler_name = os.path.basename(src_path)
    
    upscaler_dir = ensure_upscaler_directory()
    dst_path = os.path.join(upscaler_dir, upscaler_name)
    
    if os.path.exists(src_path) and not os.path.exists(dst_path):
        try:
            shutil.copy2(src_path, dst_path)
            print(f"Copied upscaler from {src_path} to {dst_path}")
            return dst_path
        except Exception as e:
            print(f"Error copying upscaler: {e}")
    
    return src_path if os.path.exists(src_path) else None

def install_upscaler_dependencies():
    """Install dependencies required for custom upscalers"""
    try:
        # Check if dependencies are already installed
        try:
            import basicsr
            import realesrgan
            print("Upscaler dependencies already installed")
            return True
        except ImportError:
            pass
        
        print("Installing upscaler dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "basicsr", "realesrgan"])
        print("Upscaler dependencies installed successfully")
        return True
    except Exception as e:
        print(f"Error installing upscaler dependencies: {e}")
        return False

def setup_upscaler(upscaler_name):
    """Set up an upscaler for use with SUPIR"""
    # Install dependencies
    if not install_upscaler_dependencies():
        print("Failed to install upscaler dependencies")
        return None
    
    # Find the upscaler file
    upscaler_path = find_upscaler_file(upscaler_name)
    if not upscaler_path:
        print(f"Could not find upscaler file: {upscaler_name}")
        return None
    
    # Copy to standard location
    upscaler_path = copy_upscaler_to_standard_location(upscaler_path)
    
    return upscaler_path

if __name__ == "__main__":
    # If run directly, try to set up the upscaler specified as an argument
    if len(sys.argv) > 1:
        upscaler_name = sys.argv[1]
        result = setup_upscaler(upscaler_name)
        if result:
            print(f"Upscaler set up successfully: {result}")
        else:
            print(f"Failed to set up upscaler: {upscaler_name}")
    else:
        print("Please specify an upscaler file name")
