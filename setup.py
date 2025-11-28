"""
XENO AI Assistant - Setup Configuration
"""

from pathlib import Path

from setuptools import find_packages, setup

# Read README for long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="XENO-ai-assistant",
    version="1.0.0",
    author="XENO Development Team",
    author_email="dev@XENO-ai.com",
    description="A fully-featured, Iron Man-inspired personal AI assistant with enterprise capabilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/navaraja20/XENO-ai-assistant",
    project_urls={
        "Bug Reports": "https://github.com/navaraja20/XENO-ai-assistant/issues",
        "Source": "https://github.com/navaraja20/XENO-ai-assistant",
        "Documentation": "https://navaraja20.github.io/XENO-ai-assistant",
    },
    packages=find_packages(include=["src", "src.*"]),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: Microsoft :: Windows",
        "Environment :: Console",
        "Environment :: Win32 (MS Windows)",
    ],
    python_requires=">=3.9",
    install_requires=[
        "google-generativeai>=0.3.0",
        "openai>=1.0.0",
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
        "cryptography>=41.0.0",
        "PyJWT>=2.8.0",
        "pyotp>=2.9.0",
        "numpy>=1.24.0",
        "scipy>=1.11.0",
        "scikit-learn>=1.3.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-asyncio>=0.21.0",
            "pytest-benchmark>=4.0.0",
            "black>=23.11.0",
            "isort>=5.12.0",
            "flake8>=6.1.0",
            "pylint>=3.0.0",
            "mypy>=1.7.0",
            "pre-commit>=3.5.0",
            "bandit>=1.7.5",
            "safety>=2.3.0",
        ],
        "ui": [
            "PyQt5>=5.15.0",
            "customtkinter>=5.2.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "XENO=src.jarvis:main",
        ],
    },
    include_package_data=True,
    package_data={
        "src": ["*.json", "*.yaml", "*.yml"],
    },
    zip_safe=False,
    keywords="ai assistant automation jarvis productivity iot voice enterprise",
)
