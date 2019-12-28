from setuptools import setup, find_packages

setup(
    name='django-settings-manager',
    version="1.0.0",
    package_dir={'': 'src'},
    packages=find_packages('src'),
    include_package_data=True,
    install_requires=[
        "pyyaml>=5.1", "pyyaml>=5.2"
    ],
    extras_require={
        'dev': ['pytest'],
    }
)
