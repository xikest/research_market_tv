from setuptools import setup, find_packages

setup(
    name='mkt-retv',
    version='1.378',
    author='xikest',
    description='market research TV ',
    packages=find_packages(),
    python_requires='>=3.7',
    install_requires=[
        'numpy', 'pandas',
        'selenium','beautifulsoup4','requests',
        'tqdm', 'openpyxl',
        'wordcloud', 'nltk',
        'scikit-learn', 'openai',
        'matplotlib', 'seaborn', 'plotly', 'kaleido'
    ],

    entry_points={
        'console_scripts': [
            'install_env_script = my_package.install_env:main',
        ],
    },

    url='https://github.com/xikest/research_market_tv',  # GitHub 프로젝트 페이지 링크
    project_urls={
        'Source': 'https://github.com/xikest/research_market_tv',  # GitHub 프로젝트 페이지 링크
        'Bug Tracker': 'https://github.com/xikest/research_market_tv/issues',  # 버그 트래커 링크
    },
)
