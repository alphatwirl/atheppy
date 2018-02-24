from setuptools import setup, find_packages
import versioneer


long_description = """
AlphaTwirl framework for Heppy flat trees
"""

setup(
    name='atheppy',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description='AlphaTwirl framework for Heppy flat trees',
    long_description=long_description,
    author='Tai Sakuma',
    author_email='tai.sakuma@gmail.com',
    url='https://github.com/alphatwirl/atheppy',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
    ],
    packages=find_packages(exclude=['docs', 'tests']),
)
