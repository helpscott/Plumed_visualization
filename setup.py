# setup.py

from setuptools import setup, find_packages


def read_readme():
    try:
        with open("README.md", "r", encoding="utf-8") as fh:
            return fh.read()
    except FileNotFoundError:
        return ""


setup(
    name="plumed_visualization_tool",
    version="0.1.0",
    author="Shi Yuchuan",
    author_email="245780622@qq.com",
    description="Plumed Visualization and Setup Tool",
    long_description=read_readme(),
    long_description_content_type="text/markdown"
    url="xxx"

    packages=find_packages(),

    install_requires=[
        "PyQt5",
        "PyQt5_sip",
        # ... 其他依赖
    ],

    entry_points={
        'console_scripts': [
            'plumed-tool=src.main:run',
        ],
    },

    include_package_data=True,
    package_data={
        "src.style": ["*.qss"],

    },


    python_requires='>=3.6',
)
