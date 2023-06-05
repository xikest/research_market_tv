from setuptools import setup, find_packages

setup(
    name='getModelSpec',
    version='1.0.0',
    author='xikest',
    description='get model spec,',
    packages=find_packages(),
    python_requires='>=3.7',
    install_requires=[
        'numpy',
        'pandas',
    ],
    entry_points={
        'console_scripts': [
            'mycommand = mypackage.module:main',
        ],
    },
)