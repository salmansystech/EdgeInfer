from setuptools import setup, find_packages

setup(
    name="EdgeInfer",
    version="1.0.0",
    description="Deploy ML models to edge devices with automatic optimization",
    author="Salman Khan",
    author_email="salmank.fin@gmail.com",
    packages=find_packages(),
    install_requires=[
        "anthropic>=2.2.0,<3",
        "python-dotenv>=1.0.0",
        "requests>=2.31.0",
        "click>=8.1.7",
        "flask>=3.0.0",
        "flask-cors>=4.0.0",
        "onnx>=1.16.0",
        "tflite>=2.10.0",
    ],
    entry_points={
        "console_scripts": [
            "edgeinfer=src.cli:cli",
        ],
    },
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Embedded Systems",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
)
