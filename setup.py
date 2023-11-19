from setuptools import setup, find_packages

setup(
    name='getmodelspec',
    version='1.357',
    author='xikest',
    description='research TV market',
    packages=find_packages(),
    python_requires='>=3.7',
    install_requires=[
        'numpy',
        'pandas',
        'selenium',
        'beautifulsoup4',
        'tqdm',
        'openpyxl',
        'requests'
    ],

    entry_points={
        'console_scripts': [
            'install_env_script = my_package.install_env:main',
        ],
    },

    url='https://github.com/xikest/research-market-tv',  # GitHub 프로젝트 페이지 링크
    project_urls={
        'Source': 'https://github.com/xikest/research-market-tv',  # GitHub 프로젝트 페이지 링크
        'Bug Tracker': 'https://github.com/xikest/research-market-tv/issues',  # 버그 트래커 링크
    },
)
