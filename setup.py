from setuptools import setup, find_packages

with open("README.md") as stream:
    long_description = stream.read()

setup(
    name='django-settings-manager',
    version="0.0.4",
    author="Iain Hadgraft",
    author_email="ihadgraft@gmail.com",
    description="A simple, extensible YAML-based configuration strategy for Django",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ihadgraft/django-settings-manager",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    package_dir={'': 'src'},
    packages=find_packages('src'),
    include_package_data=True,
    install_requires=[
        "pyyaml>=5.1", "deepmerge"
    ],
    extras_require={
        'dev': ['pytest'],
    }
)
