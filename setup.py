from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="drone-communication",
    version="0.1.0",
    author="Akash (Mr-Beck0708)",
    author_email="your.email@example.com",  # Update with your email
    description="Post-Quantum Secure Communication System for Drones",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Mr-Beck0708/Drone_Communication",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Security :: Cryptography",
        "Topic :: System :: Networking",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
    },
    project_urls={
        "Documentation": "https://github.com/Mr-Beck0708/Drone_Communication/tree/main/docs",
        "Source": "https://github.com/Mr-Beck0708/Drone_Communication",
        "Bug Reports": "https://github.com/Mr-Beck0708/Drone_Communication/issues",
    },
    keywords="post-quantum cryptography drone uav security kyber dilithium chacha20 x448",
)
