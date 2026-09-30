from setuptools import setup, find_packages

setup(
    name="EdgeInfer",
    version="1.0.0",
    description="Deploy ML models to edge devices with automatic optimization",
    author="Salman Khan",
    author_email="salmank.fin@gmail.com",
    packages=find_packages(),
    install_requires=[
        "anthropic>=0.28.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.5.0",
        "click>=8.1.7",
        "tensorflow>=2.13.0",
        "torch>=2.0.0",
        "onnx>=1.15.0",
        "numpy>=1.24.3",
    ],
    entry_points={
        "console_scripts": [
            "edgeinfer=src.cli:cli",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Embedded Systems",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
