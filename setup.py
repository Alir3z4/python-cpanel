from setuptools import find_packages, setup


setup(
    name='cpanel',
    version=".".join(map(str, __import__('cpanel').__version__)),
    packages=['cpanel'],
    url='https://github.com/Alir3z4/python-cpanel',
    license='GNU GPL 3',
    author='Alireza Savand',
    author_email='alireza.savand@gmail.com',
    description='Python cPanel - Eating cPanel with Python',
    packages=find_packages(exclude=['tests*']),
    platforms='OS Independent',
    long_description=open('README.rst').read(),
)
