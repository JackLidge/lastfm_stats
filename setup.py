from setuptools import setup, find_packages

setup(
    name='lastfm_stats',
    version='0.1',
    description='A package to create statistics from a users last.fm',
    author='Jack Lidgley',
    license='MIT',
    url='https://github.com/JackLidge/Lastfm-Stats',
    packages=find_packages(include=['lastfm_stats', 'lastfm_stats.*']),
    install_requires=[
        'requests',
        'numpy',
        'pandas',
        'matplotlib',
        'spotipy'
    ]
)