from setuptools import find_packages, setup

setup(
    name="apixdev",
    version="0.3.2",
    description="ApiX CLI",
    keywords="docker odoo development",
    url="https://github.com/apikcloud/apix-cli",
    author="Aurelien ROY",
    author_email="roy.aurelien@gmail.com",
    license="MIT",
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 5 - Production/Stable",
        # Indicate who your project is intended for
        "Intended Audience :: Developers",
        "Environment :: Console",
        "Topic :: Software Development :: Build Tools",
        # Pick your license as you wish (should match "license" above)
        "License :: OSI Approved :: MIT License",
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        "click>=8.1.6",
        "OdooRPC>=0.9.0",
        "PyYAML>=6.0.1",
        "requests>=2.28.2",
        "requirements-parser>=0.5.0",
        "git-aggregator>=4.0",
        "packaging>=23.1",
        "pandas>=2.0.0",
    ],
    entry_points={
        "console_scripts": [
            "apix = apixdev.cli.main:cli",
        ],
    },
)
