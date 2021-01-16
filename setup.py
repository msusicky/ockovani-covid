import pathlib
from setuptools import find_packages, setup
 
# The directory containing this file
HERE = pathlib.Path(__file__).parent
 
# The text of the README file
README = (HERE / "README.md").read_text()
 
# This call to setup() does all the work
setup(
    name='ockovani',
    version='1.0.0',
    description='Ockovani app',
    long_description=README,
    long_description_content_type="text/markdown",
    url='https://www.datazeet.cz',
    packages=find_packages(exclude=("tests",)),
    install_requires=["Flask>=1.1.2","Flask-Restless>=0.16.0","Flask-SQLAlchemy>=2.0","SQLAlchemy>=1.0.2","Werkzeug>=0.16.1","psycopg2==2.7.7","markupsafe"],
    author='msusicky',
    author_email='marek@susicky.net',
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "ockovani=app.__main__:main",
        ]
    },
)