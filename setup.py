from setuptools import setup, find_packages

setup(
    name='apixdev',
    version='0.1.1',
    description='Apix Developper Toolkit',
    url='https://github.com/royaurelien/apixdev',
    author='Aurelien ROY',
    author_email='roy.aurelien@gmail.com',   
    license='BSD 2-clause', 
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click",
        "gitdb",
        "GitPython",
        "OdooRPC",
        "python-gitlab",
        "PyYAML>=6.0",
        "requests",
        "sh",
        "tqdm",
    ],
    entry_points={
        'console_scripts': [
            'apix = apixdev.cli.main:cli',
        ],
    },
)