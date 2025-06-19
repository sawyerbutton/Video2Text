#!/usr/bin/env python3
"""
Setup script for MP4ToText - Video to Text Transcription Tool
"""

import sys
import platform
from pathlib import Path
from setuptools import setup, find_packages

# Read README file
def read_readme():
    readme_path = Path(__file__).parent / "README.md"
    if readme_path.exists():
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "MP4ToText - Video to Text Transcription Tool"

# Read requirements
def read_requirements():
    req_path = Path(__file__).parent / "requirements.txt"
    if req_path.exists():
        with open(req_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Filter out comments and empty lines
        requirements = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('--'):
                # Handle platform-specific requirements
                if ';' in line:
                    pkg, condition = line.split(';', 1)
                    # Only add if condition matches current platform
                    if eval_condition(condition.strip()):
                        requirements.append(pkg.strip())
                else:
                    requirements.append(line)
        
        return requirements
    
    # Fallback basic requirements
    return [
        'openai-whisper>=20231117',
        'ffmpeg-python>=0.2.0',
        'torch>=2.0.0',
        'torchaudio>=2.0.0',
        'tqdm>=4.65.0',
        'colorama>=0.4.6',
        'pathvalidate>=3.0.0'
    ]

def eval_condition(condition):
    """Evaluate platform condition for requirements."""
    try:
        # Replace common variables
        condition = condition.replace('sys_platform', f'"{sys.platform}"')
        condition = condition.replace('python_version', f'"{sys.version_info.major}.{sys.version_info.minor}"')
        return eval(condition)
    except:
        return True  # Include by default if evaluation fails

# Platform-specific dependencies
def get_platform_dependencies():
    """Get additional dependencies based on platform."""
    deps = []
    
    if sys.platform == "win32":
        deps.extend([
            'pywin32>=306',
            'colorama>=0.4.6'  # Essential for Windows colored output
        ])
    elif sys.platform == "darwin":
        deps.extend([
            'pyobjc>=9.0'  # macOS specific
        ])
    
    return deps

# Entry points
def get_entry_points():
    """Get console entry points."""
    return {
        'console_scripts': [
            'mp4-to-text=mp4_to_text:main',
            'video2text=mp4_to_text:main',
            'v2t=mp4_to_text:main'
        ]
    }

# Classifiers
CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Intended Audience :: End Users/Desktop",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Multimedia :: Video",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
    "Topic :: Text Processing :: Linguistic",
    "Topic :: Utilities"
]

# Project URLs
PROJECT_URLS = {
    "Bug Reports": "https://github.com/your-username/Video2Text/issues",
    "Source": "https://github.com/your-username/Video2Text",
    "Documentation": "https://github.com/your-username/Video2Text/blob/main/README.md"
}

# Check Python version
if sys.version_info < (3, 9):
    print("Error: MP4ToText requires Python 3.9 or higher")
    print(f"You are using Python {sys.version_info.major}.{sys.version_info.minor}")
    sys.exit(1)

# Setup configuration
setup(
    name="mp4-to-text",
    version="1.0.0",
    author="Video2Text Team",
    author_email="contact@video2text.com",
    description="Cross-platform video to text transcription tool using OpenAI Whisper",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/Video2Text",
    project_urls=PROJECT_URLS,
    
    # Package configuration
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'core': ['*.py'],
        'config': ['*.ini'],
        'examples': ['*'],
    },
    
    # Dependencies
    python_requires=">=3.9",
    install_requires=read_requirements(),
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'black>=22.0.0',
            'flake8>=5.0.0',
            'mypy>=1.0.0'
        ],
        'gpu': [
            'torch[cuda]>=2.0.0',  # CUDA support
        ],
        'all': [
            'psutil>=5.9.0',  # System resource monitoring
            'jupyter>=1.0.0',  # Jupyter notebook support
        ]
    },
    
    # Entry points
    entry_points=get_entry_points(),
    
    # Metadata
    classifiers=CLASSIFIERS,
    keywords=[
        "video", "transcription", "whisper", "speech-to-text", 
        "mp4", "audio", "ai", "machine-learning", "cross-platform"
    ],
    license="MIT",
    
    # Platform specific
    platforms=["Windows", "macOS", "Linux"],
    
    # Additional metadata
    zip_safe=False,
    
    # Custom commands
    cmdclass={},
)

# Post-installation message
def print_installation_info():
    """Print post-installation information."""
    print("\n" + "="*60)
    print("MP4ToText Installation Complete!")
    print("="*60)
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version}")
    print("\nNext steps:")
    print("1. Install FFmpeg if not already installed:")
    
    if sys.platform == "win32":
        print("   - Download from: https://ffmpeg.org/download.html")
        print("   - Or use: choco install ffmpeg")
    elif sys.platform == "darwin":
        print("   - Use Homebrew: brew install ffmpeg")
    else:
        print("   - Ubuntu/Debian: sudo apt install ffmpeg")
        print("   - CentOS/RHEL: sudo yum install ffmpeg")
    
    print("\n2. Test the installation:")
    print("   mp4-to-text --system-info")
    print("   mp4-to-text --list-models")
    
    print("\n3. Basic usage:")
    print("   mp4-to-text -i /path/to/videos -o /path/to/texts")
    
    print("\n4. For help:")
    print("   mp4-to-text --help")
    
    print("\nDocumentation: https://github.com/your-username/Video2Text")
    print("="*60)

if __name__ == "__main__":
    # Run setup
    try:
        setup()
        print_installation_info()
    except Exception as e:
        print(f"Installation failed: {e}")
        sys.exit(1) 