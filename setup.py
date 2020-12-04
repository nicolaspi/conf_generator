import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="conf-generator",
    version="1.0.1",
    author="Nicolas Pinchaud",
    author_email="nicolas.pinchaud@gmail.com",
    description="Conf-Generator is a tool for specifying and exploring hyper-parameters sets "
                "in Machine Learning pipelines defined through configuration files.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nicolaspi/conf_generator",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
          'pyyaml',
    ],
)
