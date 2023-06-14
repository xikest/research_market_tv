from setuptools import setup, find_packages

setup(
    name='getmodelspec',
    version='1.0.376',
    author='xikest',
    description='get model spec,',
    packages=find_packages(),
    python_requires='>=3.7',
    install_requires=[
        'numpy',
        'pandas',
        'selenium',
        'bs4'
    ],
    entry_points={
        'console_scripts': [
            'mycommand = mypackage.module:main',
        ],
    },

    url='https://github.com/xikest/Research-on-the-TV-market',  # GitHub 프로젝트 페이지 링크
    project_urls={
        'Source': 'https://github.com/xikest/Research-on-the-TV-market',  # GitHub 프로젝트 페이지 링크
        'Bug Tracker': 'https://github.com/xikest/Research-on-the-TV-market/issues',  # 버그 트래커 링크
    },
)