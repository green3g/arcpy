from setuptools import setup, find_packages

setup(
    name='arcpy_dbgrate',
    author='roemhildtg',
    version='0.5.10',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'mako',
        'dbgrate',
    ],
    entry_points='''
        [console_scripts]
        arcpy=arcpy_dbgrate.main:cli
    '''
)