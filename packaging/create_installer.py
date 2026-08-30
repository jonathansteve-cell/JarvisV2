"""
Jarvis V2 - Complete Installer Creator
=======================================
Creates a professional Windows installer with all components.

This script:
1. Builds the executable with PyInstaller
2. Creates installer images
3. Compiles the Inno Setup installer
4. Creates a portable ZIP package

Usage:
    python packaging/create_installer.py
"""

from __future__ import annotations

import os
import sys
import shutil
import subprocess
from pathlib import Path
from datetime import datetime


class InstallerCreator:
    """Creates the Jarvis V2 installer."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.packaging_dir = self.project_root / "packaging"
        self.dist_dir = self.project_root / "dist"
        self.build_dir = self.project_root / "build"
        
        # Application info
        self.app_name = "JarvisV2"
        self.app_version = "2.0.0"
        self.app_publisher = "jonathansteve-cell"
        
    def print_header(self):
        """Print the build header."""
        print("\n" + "=" * 60)
        print("  JARVIS V2 - INSTALLER CREATOR")
        print("=" * 60)
        print(f"\n  Version: {self.app_version}")
        print(f"  Publisher: {self.app_publisher}")
        print(f"  Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n" + "=" * 60 + "\n")
    
    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are installed."""
        print("[1/6] Checking prerequisites...")
        
        # Check Python
        print(f"  ✓ Python {sys.version.split()[0]}")
        
        # Check PyInstaller
        try:
            import PyInstaller
            print(f"  ✓ PyInstaller {PyInstaller.__version__}")
        except ImportError:
            print("  ✗ PyInstaller not found. Installing...")
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], 
                         capture_output=True)
            print("  ✓ PyInstaller installed")
        
        # Check Pillow
        try:
            from PIL import Image
            print("  ✓ Pillow (Image processing)")
        except ImportError:
            print("  ✗ Pillow not found. Installing...")
            subprocess.run([sys.executable, "-m", "pip", "install", "pillow"], 
                         capture_output=True)
            print("  ✓ Pillow installed")
        
        # Check Inno Setup
        iscc_paths = [
            Path(os.environ.get("ProgramFiles", "")) / "Inno Setup 6" / "ISCC.exe",
            Path(os.environ.get("ProgramFiles(x86)", "")) / "Inno Setup 6" / "ISCC.exe",
        ]
        
        self.iscc_path = None
        for path in iscc_paths:
            if path.exists():
                self.iscc_path = path
                print(f"  ✓ Inno Setup 6 found")
                break
        
        if not self.iscc_path:
            print("  ⚠ Inno Setup 6 not found (installer will be skipped)")
            print("    Download from: https://jrsoftware.org/isdl.php")
        
        print()
        return True
    
    def clean_build_dirs(self):
        """Clean build directories."""
        print("[2/6] Cleaning build directories...")
        
        dirs_to_clean = [self.dist_dir, self.build_dir]
        for dir_path in dirs_to_clean:
            if dir_path.exists():
                shutil.rmtree(dir_path)
                print(f"  ✓ Cleaned: {dir_path.name}")
        
        print()
    
    def create_icon(self):
        """Create application icon."""
        print("[3/6] Creating application icon...")
        
        try:
            # Run make_icon.py
            result = subprocess.run(
                [sys.executable, str(self.packaging_dir / "make_icon.py")],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("  ✓ Icon created successfully")
            else:
                print(f"  ⚠ Icon creation warning: {result.stderr}")
        except Exception as e:
            print(f"  ⚠ Icon creation failed: {e}")
        
        # Create installer images
        try:
            result = subprocess.run(
                [sys.executable, str(self.packaging_dir / "create_installer_images.py")],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("  ✓ Installer images created")
            else:
                print(f"  ⚠ Image creation warning: {result.stderr}")
        except Exception as e:
            print(f"  ⚠ Image creation failed: {e}")
        
        print()
    
    def build_executable(self):
        """Build the executable with PyInstaller."""
        print("[4/6] Building executable with PyInstaller...")
        print("  This may take 2-5 minutes...\n")
        
        # Run PyInstaller
        spec_file = self.packaging_dir / "jarvis.spec"
        
        result = subprocess.run(
            [
                sys.executable, "-m", "PyInstaller",
                "--noconfirm",
                "--clean",
                str(spec_file)
            ],
            cwd=str(self.project_root)
        )
        
        if result.returncode != 0:
            print("  ✗ Build failed!")
            return False
        
        # Create runtime directories
        app_dir = self.dist_dir / self.app_name
        if app_dir.exists():
            dirs = ['data', 'logs', 'screenshots', 'documents', 'research']
            for d in dirs:
                (app_dir / d).mkdir(exist_ok=True)
            
            # Copy config files
            config_src = self.project_root / "config"
            config_dst = app_dir / "config"
            if config_src.exists():
                if config_dst.exists():
                    shutil.rmtree(config_dst)
                shutil.copytree(config_src, config_dst)
            
            # Copy .env.example
            env_example = self.project_root / ".env.example"
            if env_example.exists():
                shutil.copy2(env_example, app_dir / ".env.example")
            
            # Copy README
            readme = self.project_root / "README.md"
            if readme.exists():
                shutil.copy2(readme, app_dir / "README.md")
            
            print(f"  ✓ Executable built: {app_dir / self.app_name}.exe")
        else:
            print("  ✗ Build directory not found!")
            return False
        
        print()
        return True
    
    def create_installer(self):
        """Create the installer with Inno Setup."""
        print("[5/6] Creating installer...")
        
        if not self.iscc_path:
            print("  ⚠ Inno Setup not found, skipping installer creation")
            print("  ✓ Portable app available at: dist/JarvisV2/")
            print()
            return False
        
        # Create installer output directory
        installer_dir = self.dist_dir / "installer"
        installer_dir.mkdir(exist_ok=True)
        
        # Run Inno Setup
        iss_file = self.packaging_dir / "installer.iss"
        
        result = subprocess.run(
            [str(self.iscc_path), "/Q", str(iss_file)],
            cwd=str(self.project_root)
        )
        
        if result.returncode != 0:
            print("  ✗ Installer creation failed!")
            return False
        
        installer_file = installer_dir / f"{self.app_name}-Setup.exe"
        if installer_file.exists():
            size_mb = installer_file.stat().st_size / (1024 * 1024)
            print(f"  ✓ Installer created: {installer_file}")
            print(f"  ✓ Size: {size_mb:.1f} MB")
        else:
            print("  ✗ Installer file not found!")
            return False
        
        print()
        return True
    
    def create_portable_zip(self):
        """Create a portable ZIP package."""
        print("[6/6] Creating portable ZIP package...")
        
        app_dir = self.dist_dir / self.app_name
        if not app_dir.exists():
            print("  ✗ App directory not found!")
            return False
        
        # Create ZIP
        zip_file = self.dist_dir / f"{self.app_name}-Portable-{self.app_version}.zip"
        shutil.make_archive(
            str(zip_file).replace('.zip', ''),
            'zip',
            str(app_dir.parent),
            str(app_dir.name)
        )
        
        if zip_file.exists():
            size_mb = zip_file.stat().st_size / (1024 * 1024)
            print(f"  ✓ Portable ZIP: {zip_file}")
            print(f"  ✓ Size: {size_mb:.1f} MB")
        else:
            print("  ✗ ZIP creation failed!")
            return False
        
        print()
        return True
    
    def print_summary(self):
        """Print build summary."""
        print("=" * 60)
        print("  BUILD COMPLETE!")
        print("=" * 60)
        print("\n  Output files:\n")
        
        # List output files
        outputs = [
            (self.dist_dir / self.app_name / f"{self.app_name}.exe", "Desktop Application"),
            (self.dist_dir / "installer" / f"{self.app_name}-Setup.exe", "Windows Installer"),
            (self.dist_dir / f"{self.app_name}-Portable-{self.app_version}.zip", "Portable Package"),
        ]
        
        for file_path, description in outputs:
            if file_path.exists():
                size_mb = file_path.stat().st_size / (1024 * 1024)
                print(f"  ✓ {description}:")
                print(f"    {file_path}")
                print(f"    Size: {size_mb:.1f} MB\n")
            else:
                print(f"  ✗ {description}: Not created\n")
        
        print("=" * 60)
        print("\n  Distribution options:")
        print("  1. Share the installer (.exe) for easy installation")
        print("  2. Share the portable ZIP for no-install usage")
        print("  3. Share the dist/JarvisV2 folder directly\n")
        print("=" * 60 + "\n")
    
    def run(self):
        """Run the complete build process."""
        self.print_header()
        
        if not self.check_prerequisites():
            return False
        
        self.clean_build_dirs()
        self.create_icon()
        
        if not self.build_executable():
            return False
        
        self.create_installer()
        self.create_portable_zip()
        self.print_summary()
        
        return True


def main():
    """Main entry point."""
    creator = InstallerCreator()
    success = creator.run()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
