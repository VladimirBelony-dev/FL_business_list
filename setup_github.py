#!/usr/bin/env python3
"""
GitHub Setup Helper Script
This script helps you set up your repository for GitHub upload
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Run a command and return success status"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def check_git_installed():
    """Check if Git is installed"""
    try:
        result = subprocess.run(['git', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Git is installed: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ Git is not installed")
    print("Please install Git from: https://git-scm.com/downloads")
    return False

def check_git_config():
    """Check if Git is configured"""
    try:
        # Check user name
        name_result = subprocess.run(['git', 'config', 'user.name'], capture_output=True, text=True)
        email_result = subprocess.run(['git', 'config', 'user.email'], capture_output=True, text=True)
        
        if name_result.returncode == 0 and email_result.returncode == 0:
            print(f"✅ Git configured: {name_result.stdout.strip()} <{email_result.stdout.strip()}>")
            return True
    except:
        pass
    
    print("❌ Git is not configured")
    print("Please run these commands:")
    print('git config --global user.name "Your Name"')
    print('git config --global user.email "your.email@example.com"')
    return False

def initialize_git_repo():
    """Initialize Git repository"""
    if Path('.git').exists():
        print("✅ Git repository already initialized")
        return True
    
    return run_command('git init', 'Initializing Git repository')

def add_files():
    """Add files to Git"""
    return run_command('git add .', 'Adding files to Git')

def create_initial_commit():
    """Create initial commit"""
    commit_message = '''Initial commit: Florida Corporation Data Processing System

- Complete data extraction pipeline for 8M+ records
- Advanced fuzzy matching with 83.1% accuracy  
- Professional Excel formatting with Corps styling
- Comprehensive documentation and testing suite
- Status code decoding (AFLAL = Active Florida LLC)'''
    
    return run_command(f'git commit -m "{commit_message}"', 'Creating initial commit')

def show_git_status():
    """Show Git status"""
    print("\n📊 Git Status:")
    subprocess.run(['git', 'status'], shell=True)

def show_next_steps():
    """Show next steps for GitHub upload"""
    print("\n" + "="*60)
    print("🎉 LOCAL GIT REPOSITORY READY!")
    print("="*60)
    print("\n📋 Next steps to upload to GitHub:")
    print("\n1. Go to https://github.com and create a new repository:")
    print("   - Repository name: florida-corp-processor")
    print("   - Description: Advanced data processing pipeline for Florida corporation records")
    print("   - Make it Public")
    print("   - Don't initialize with README (we already have one)")
    
    print("\n2. Connect your local repository to GitHub:")
    print("   git remote add origin https://github.com/YOURUSERNAME/florida-corp-processor.git")
    print("   git branch -M main")
    print("   git push -u origin main")
    
    print("\n3. Replace YOURUSERNAME with your actual GitHub username")
    
    print("\n📚 For detailed instructions, see GITHUB_SETUP_GUIDE.md")
    
    print("\n🔍 Current repository status:")
    subprocess.run(['git', 'log', '--oneline', '-1'], shell=True)

def main():
    """Main setup function"""
    print("🚀 GitHub Setup Helper")
    print("="*40)
    
    # Check if we're in the right directory
    if not Path('README.md').exists():
        print("❌ README.md not found. Please run this script from your project directory.")
        return False
    
    # Check Git installation
    if not check_git_installed():
        return False
    
    # Check Git configuration
    if not check_git_config():
        print("\n⚠️  Please configure Git first, then run this script again.")
        return False
    
    # Initialize Git repository
    if not initialize_git_repo():
        return False
    
    # Add files
    if not add_files():
        return False
    
    # Create initial commit
    if not create_initial_commit():
        return False
    
    # Show status
    show_git_status()
    
    # Show next steps
    show_next_steps()
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Setup completed successfully!")
    else:
        print("\n❌ Setup failed. Please check the errors above.")
    sys.exit(0 if success else 1)

