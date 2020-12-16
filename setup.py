#   VIM SETTINGS: {{{3
#   vim: set tabstop=4 modeline modelines=10 foldmethod=marker:
#   vim: set foldlevel=2 foldcolumn=3: 
#   }}}1

import re
from distutils.core import setup
from setuptools import setup

version = re.search(
    '^__version__\s*=\s*"(.*)"',
    open('dtscan/__main__.py').read(),
    re.M
    ).group(1)


with open("README.md", "rb") as f:
    long_descr = f.read().decode("utf-8")


#setup(
#    name = "cmdline-bootstrap",
#    packages = ["bootstrap"],
#    entry_points = {
#        "console_scripts": ['bootstrap = bootstrap.bootstrap:main']
#        },
#    version = version,
#    description = "Python command line application bare bones template.",
#    long_description = long_descr,
#    author = "Jan-Philip Gehrcke",
#    author_email = "jgehrcke@googlemail.com",
#    url = "http://gehrcke.de/2014/02/distributing-a-python-command-line-application",
#    )

test_depend = [ 
    'pytest'
    'pandas'
    'tzlocal'
    'pytz'
    'dateparser'
]

setup(
    name="taskblock-reader",
    version=version,
    author="Matthew Davis",
    author_email="mld.0@protonmail.com",
    description="",
    long_description=long_descr,
    packages = ['readblock', 'tests'],
    tests_require=test_depend,
    entry_points={
        'console_scripts': [ 'taskblock-reader = readblock.__main__:cliscan' ],
    }
)





