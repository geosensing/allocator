from setuptools import setup, find_packages
from setuptools.command.develop import develop
from setuptools.command.install import install
from setuptools.command.test import test as TestCommand

from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()


class PostDevelopCommand(develop):
    """Post-installation for development mode."""
    def run(self):
        print("TODO: PostDevelopCommand")
        develop.run(self)


class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        print("TODO: PostInstallCommand")
        install.run(self)


class Tox(TestCommand):
    user_options = [('tox-args=', 'a', "Arguments to pass to tox")]
    
    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.tox_args = None
    
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True
    
    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import tox
        import shlex
        args = self.tox_args
        if args:
            args = shlex.split(self.tox_args)
        tox.cmdline(args=args)


setup(
    name='allocator',

    # Versions should comply with PEP440.
    version='0.2.0',

    description='Optimally Allocate Geographically Distributed Tasks',
    long_description=long_description,
    long_description_content_type='text/x-rst',  # Added content type for PyPI

    # The project's main homepage.
    url='https://github.com/soodoku/allocator',

    # Author details
    author='Suriyan Laohaprapanon, Gaurav Sood',
    author_email='suriyant@gmail.com, gsood07@gmail.com',

    # Choose your license
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',  # Updated to Beta since it's more mature now

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',  # Added audience

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities'
    ],

    # What does your project relate to?
    keywords='routing shortest path geographic allocation optimization',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=['data', 'docs', 'tests', 'scripts']),

    # List run-time dependencies here.
    python_requires='>=3.6',  # Specify minimum Python version
    install_requires=[
        'pandas>=1.0.0',
        'numpy>=1.20.0',
        'matplotlib>=3.3.0',
        'utm>=0.7.0',
        'networkx>=2.6.0',
        'googlemaps>=4.0.0',
        'polyline>=1.4.0',
        'haversine>=2.5.0',
        'folium>=0.12.0',
        'scipy>=1.7.0'
    ],

    # List additional groups of dependencies here
    extras_require={
        'dev': [
            'check-manifest',
            'flake8',
            'black',
            'isort',
        ],
        'test': [
            'coverage',
            'pytest',
            'pytest-cov',
        ],
        'docs': [
            'sphinx',
            'sphinx_rtd_theme',
        ],
    },

    # If there are data files included in your packages
    package_data={
        'allocator': [
            'examples/*.csv',
            'examples/*.png',
            'examples/sort-by-distance/*.csv',
            'examples/sort-by-distance/*.png',
            'examples/kmeans/*.csv',
            'examples/kmeans/*.png',
            'examples/KaHIP/*.csv',
            'examples/KaHIP/*.png',
            'examples/TSP-buffoon/*.svg',
            'examples/TSP-kmeans/*.svg',
            'examples/TSP-ortools-kmeans/*.png',
            'examples/TSP-ortools-kmeans/map/*.html',
            'examples/TSP-ortools-buffoon/delhi/*.png',
            'examples/TSP-ortools-buffoon/chonburi/*.png',
            'examples/GM-buffoon/chonburi/*.png',
            'examples/GM-buffoon/delhi/*.png',
            'examples/OSRM-buffoon/*.html',
            'examples/compare-kahip-kmeans/*.csv',
            'tests/*.csv',
        ],
    },

    # To provide executable scripts
    entry_points={
        'console_scripts': [
            'sort_by_distance=allocator.sort_by_distance:main',
            'cluster_kmeans=allocator.cluster_kmeans:main',
            'cluster_kahip=allocator.cluster_kahip:main',
            'shortest_path_mst_tsp=allocator.shortest_path_mst_tsp:main',
            'shortest_path_ortools=allocator.shortest_path_ortools:main',
            'shortest_path_gm=allocator.shortest_path_gm:main',
            'shortest_path_osrm=allocator.shortest_path_osrm:main',
            'compare_kahip_kmeans=allocator.compare_kahip_kmeans:main',
        ],
    },
    cmdclass={
        'develop': PostDevelopCommand,
        'install': PostInstallCommand,
        'test': Tox,
    },
    tests_require=['tox', 'pytest'],
    project_urls={  # Added project URLs for better PyPI page
        'Bug Reports': 'https://github.com/geosensing/allocator/issues',
        'Source': 'https://github.com/geosensing/allocator',
    },
)