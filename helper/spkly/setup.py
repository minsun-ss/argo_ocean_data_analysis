from setuptools import setup

setup(name='spkly',
      version='0.1',
      description='sparklines for pandas dataframes',
      url='https://github.com/shsung-umich/sparkly',
      author='SS',
      author_email='sungsh@umich.edu',
      license='MIT',
      packages=['spkly'],
      python_requires='>-3.6',
      install_requires=[
            'pandas',
            'numpy',
            'ipython'])