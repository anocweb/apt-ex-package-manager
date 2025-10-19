#!/usr/bin/env python3
"""Setup script for Apt-Ex Package Manager"""

from setuptools import setup, find_packages
import os

# Read requirements
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

# Read README
with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='apt-ex-package-manager',
    version='0.1.0',
    description='Modern graphical package manager for Linux',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Apt-Ex Team',
    url='https://github.com/yourusername/apt-ex-package-manager',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=requirements,
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'apt-ex=main:main',
        ],
    },
    data_files=[
        # Install plugins to system location
        ('/usr/share/apt-ex-package-manager/plugins', [
            'src/controllers/plugins/apt_plugin.py',
            'src/controllers/plugins/flatpak_plugin.py',
            'src/controllers/plugins/appimage_plugin.py',
            'src/controllers/plugins/__init__.py',
        ]),
        # Install UI files
        ('/usr/share/apt-ex-package-manager/ui', [
            'src/ui/main_window.ui',
            'src/ui/category_panel.ui',
            'src/ui/installed_panel.ui',
            'src/ui/updates_panel.ui',
            'src/ui/settings_panel.ui',
            'src/ui/about_panel.ui',
        ]),
        # Install icons
        ('/usr/share/apt-ex-package-manager/icons', [
            'src/icons/app-icon.svg',
            'src/icons/app-icon-dark.svg',
        ]),
        # Desktop file
        ('/usr/share/applications', ['apt-ex-package-manager.desktop']),
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: System :: Software Distribution',
    ],
)
