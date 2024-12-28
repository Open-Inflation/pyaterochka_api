from setuptools import setup, find_packages

setup(
    name='pyaterochka_api',
    version='0.1.2',
    packages=find_packages(),
    install_requires=[
        'aiohttp',
        'fake-useragent',
        'tqdm'
    ],
    author='Miskler',
    description='A Python API client for Pyaterochka store catalog',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Open-Inflation/pyaterochka_api',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
)
