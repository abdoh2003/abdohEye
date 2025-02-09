from setuptools import setup, find_packages

setup(
    name="abdohEye",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'psutil>=5.8.0',
        'cryptography>=36.0.0',
    ],
    entry_points={
        'console_scripts': [
            'abdohEye = abdoheye.monitor:main',
        ],
    },
    author="Abdelrahman Abdoh",
    description="System Resource Monitor with Forensic Logging",
    keywords="system monitoring forensic logging",
    url="https://github.com/abdoh2003/abdohEye.git",
)