from setuptools import setup, find_packages

setup(name='conf-generator',
      version='1.0.0',
      description='Conf-Generator is a tool for specifying and exploring hyper-parameters sets in Machine Learning pipelines defined through configuration files.',
      packages=find_packages(),
      setup_requires=['pytest-runner'],
      tests_require=['pytest'],
      include_package_data=True
      )