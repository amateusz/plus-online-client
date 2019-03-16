from setuptools import find_packages
from setuptools import setup

setup(
    name='plus-online-client',
    version='1.0',
    packages=find_packages(),
    # packages=[''],
    url='https://github.com/amateusz/plus-online-client',
    license='LGPL',
    author='amateusz',
    author_email='grzywomat@gmail.com',
    description='connect with Plus GSM API and fetch data plan details',
    requires=[
        'notify2'
    ]
)
