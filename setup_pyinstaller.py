# PyInstaller build script
from PyInstaller.__main__ import run

if __name__ == '__main__':
    opts = [
        '--name=TweetCollector',
        '--onefile',
        'run_app.py'
    ]
    run(opts)
