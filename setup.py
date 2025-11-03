from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="pimst",
    version="0.22.0",
    author="[Your Name]",
    author_email="hello@pimst.io",
    description="Ultra-fast TSP solver using gravity-guided heuristics - 147x faster than LKH",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/[your-username]/pimst-solver",
    project_urls={
        "Bug Tracker": "https://github.com/[your-username]/pimst-solver/issues",
        "Documentation": "https://github.com/[your-username]/pimst-solver/docs",
        "Source Code": "https://github.com/[your-username]/pimst-solver",
        "Paper": "https://arxiv.org/abs/pending",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=23.0",
            "flake8>=6.0",
            "mypy>=1.0",
        ],
        "viz": [
            "matplotlib>=3.5",
            "seaborn>=0.12",
        ],
    },
    entry_points={
        "console_scripts": [
            "pimst=pimst.cli:main",
        ],
    },
    keywords=[
        "tsp",
        "traveling salesman problem",
        "optimization",
        "heuristic",
        "routing",
        "logistics",
        "operations research",
        "combinatorial optimization",
    ],
)
