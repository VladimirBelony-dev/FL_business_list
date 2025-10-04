#!/usr/bin/env python3
"""
Example workflow demonstrating the complete Florida Corporation Data Processing Pipeline

This script shows how to use the system step by step with sample data.
"""

import os
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime

def check_requirements():
    """Check if all required files and packages are available"""
    print("🔍 Checking requirements...")
    
    # Check Python packages
    required_packages = ['pandas', 'numpy', 'rapidfuzz', 'openpyxl']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    # Check data files
    required_files = [
        'Corps 10-2-25.xlsx',
        'cordata0.txt',  # At least one cordata file
        'npcordata0.txt'  # At least one npcordata file
    ]
    
    missing_files = []
    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file}")
        else:
            missing_files.append(file)
            print(f"❌ {file}")
    
    if missing_files:
        print(f"\n❌ Missing files: {', '.join(missing_files)}")
        print("Please ensure all data files are in the current directory")
        return False
    
    print("\n✅ All requirements met!")
    return True

def run_extraction():
    """Run the data extraction step"""
    print("\n" + "="*60)
    print("📊 STEP 1: Data Extraction")
    print("="*60)
    
    try:
        # Import and run extraction
        from extract_officers_full import main as extract_main
        print("Running data extraction...")
        extract_main()
        print("✅ Data extraction completed!")
        return True
    except Exception as e:
        print(f"❌ Data extraction failed: {e}")
        return False

def run_matching():
    """Run the document matching step"""
    print("\n" + "="*60)
    print("🔍 STEP 2: Document Matching")
    print("="*60)
    
    try:
        # Import and run matching
        from document_number_matcher import main as match_main
        print("Running document matching...")
        match_main()
        print("✅ Document matching completed!")
        return True
    except Exception as e:
        print(f"❌ Document matching failed: {e}")
        return False

def run_formatting():
    """Run the formatting step"""
    print("\n" + "="*60)
    print("🎨 STEP 3: Data Formatting")
    print("="*60)
    
    try:
        # Import and run formatting
        from fill_officer_address_data import main as format_main
        print("Running data formatting...")
        format_main()
        print("✅ Data formatting completed!")
        return True
    except Exception as e:
        print(f"❌ Data formatting failed: {e}")
        return False

def show_results():
    """Show the results of the processing"""
    print("\n" + "="*60)
    print("📋 RESULTS SUMMARY")
    print("="*60)
    
    # Find the latest files
    csv_files = list(Path('.').glob('new_officer_sheet_*.csv'))
    match_files = list(Path('.').glob('fast_document_matches_*.xlsx'))
    format_files = list(Path('.').glob('Corps_10-2-25_FORMATTED_*.xlsx'))
    
    if csv_files:
        latest_csv = max(csv_files, key=os.path.getctime)
        print(f"📄 Extracted data: {latest_csv}")
        
        # Show sample of extracted data
        try:
            df = pd.read_csv(latest_csv, nrows=5)
            print(f"   Records: {len(pd.read_csv(latest_csv)):,}")
            print(f"   Columns: {', '.join(df.columns.tolist())}")
        except Exception as e:
            print(f"   Error reading file: {e}")
    
    if match_files:
        latest_match = max(match_files, key=os.path.getctime)
        print(f"🔍 Match results: {latest_match}")
        
        # Show matching statistics
        try:
            df = pd.read_excel(latest_match, sheet_name='Summary')
            print("   Match Statistics:")
            for _, row in df.iterrows():
                print(f"     {row['Metric']}: {row['Value']}")
        except Exception as e:
            print(f"   Error reading match file: {e}")
    
    if format_files:
        latest_format = max(format_files, key=os.path.getctime)
        print(f"🎨 Formatted output: {latest_format}")
        
        # Show file size
        size_mb = os.path.getsize(latest_format) / (1024 * 1024)
        print(f"   File size: {size_mb:.1f} MB")
    
    print("\n🎉 Processing pipeline completed successfully!")
    print("\n📚 Next steps:")
    print("1. Review the output files")
    print("2. Check the match quality in the Excel files")
    print("3. Use the formatted data for your business needs")

def main():
    """Main workflow function"""
    print("🚀 Florida Corporation Data Processing Pipeline")
    print("   Example Workflow")
    print("="*60)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Requirements not met. Please fix the issues above.")
        return False
    
    # Run the pipeline steps
    steps = [
        ("Data Extraction", run_extraction),
        ("Document Matching", run_matching),
        ("Data Formatting", run_formatting)
    ]
    
    for step_name, step_function in steps:
        print(f"\n🔄 Running {step_name}...")
        if not step_function():
            print(f"\n❌ Pipeline failed at {step_name}")
            return False
    
    # Show results
    show_results()
    
    print(f"\n⏱️  Total time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

