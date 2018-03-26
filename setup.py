from setuptools import setup

from distutils.extension import Extension
from Cython.Distutils import build_ext

ext_modules = [Extension('crossdist',
              ['larana/crossdist.pyx'],
                         )
               ]

setup(name='larana',
      version='0.31',
      description='larsoft data interface',
      url='',
      author='maluethi',
      author_email='maluethi@example.com',
      license='MIT',
      packages=['larana'],
      zip_safe=False,
      cmdclass={'build_ext': build_ext},
      ext_modules = ext_modules)