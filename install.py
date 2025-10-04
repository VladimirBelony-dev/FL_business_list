#!/usr/bin/env python3
"""
Quick installation script for Florida Corporation Data Processing System
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python version {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_requirements():
    """Install required packages"""
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found")
        return False
    
    return run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Installing required packages"
    )

def verify_installation():
    """Verify that all packages are installed correctly"""
    print("\n🔍 Verifying installation...")
    
    packages = [
        "pandas", "numpy", "rapidfuzz", "openpyxl", 
        "beautifulsoup4", "requests", "lxml"
    ]
    
    for package in packages:
        try:
            __import__(package)
            print(f"✅ {package} is available")
        except ImportError:
            print(f"❌ {package} is not available")
            return False
    
    return True

def main():
    """Main installation function"""
    print("=" * 60)
    print("🚀 Florida Corporation Data Processing System")
    print("   Installation Script")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        print("\n❌ Installation failed. Please check the error messages above.")
        sys.exit(1)
    
    # Verify installation
    if not verify_installation():
        print("\n❌ Verification failed. Some packages may not be installed correctly.")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("🎉 Installation completed successfully!")
    print("=" * 60)
    print("\n📋 Next steps:")
    print("1. Place your data files in the project directory:")
    print("   - cordata0.txt through cordata9.txt")
    print("   - npcordata0.txt through npcordata9.txt")
    print("   - Corps 10-2-25.xlsx")
    print("\n2. Run the processing pipeline:")
    print("   python extract_officers_full.py")
    print("   python document_number_matcher.py")
    print("   python fill_officer_address_data.py")
    print("\n3. Check the output files:")
    print("   - new_officer_sheet_*.csv")
    print("   - fast_document_matches_*.xlsx")
    print("   - Corps_10-2-25_FORMATTED*.xlsx")
    print("\n📚 For detailed instructions, see README.md")
    print("🔧 For technical details, see TECHNICAL_DOCS.md")

if __name__ == "__main__":
    main()

