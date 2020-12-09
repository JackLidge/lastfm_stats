from setuptools import setup, find_packages

setup(
    name='lastfm_stats',
    version='0.1',
    description='A package to create statistics from a users last.fm',
    author='Jack Lidgley',
    license='MIT',
    url='https://github.com/JackLidge/Lastfm-Stats',
    download_url='https://github.com/JackLidge/lastfm_stats/archive/v0.1.tar.gz',
    packages=find_packages(include=['lastfm_stats', 'lastfm_stats.*']),
    classifiers=[
        '''
        Development Status :: 3 - Alpha
        Intended Audience :: Developers
        License :: MIT
        Programming Language :: Python
        Programming Language :: Python :: 3.7
        Programming Language :: Python :: 3.8
        Operating System :: Microsoft :: Windows
        Operating System :: Unix
        '''
    ],
    install_requires=[
        'requests',
        'pandas',
    ]
)