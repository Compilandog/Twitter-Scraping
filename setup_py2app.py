from setuptools import setup

APP = ['run_app.py']
DATA_FILES = ['templates', 'static', 'lists.json']
OPTIONS = {'argv_emulation': True, 'packages': ['flask', 'snscrape', 'pandas', 'fpdf']}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
