from setuptools import setup

version = '0.1'

setup(name='wee',
      version=version,
      description="like itty but uses webob request, response and exception objects",
      long_description=open('README.rst').read(),
      classifiers=[], 
      keywords='web wsgi',
      author='whit morriss and matt george',
      author_email='whit at nocoast dot us',
      url='',
      license='MIT',
      include_package_data=True,
      zip_safe=True,
      py_modules=['wee'],
      install_requires=["webob", "venusian"],
      entry_points=""" """,
      )
