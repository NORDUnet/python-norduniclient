from setuptools import setup, find_packages

version = '1.3.4'

requires = [
    'neo4j-driver<2.0',
]

testing_requires = [
    'nose',
    'coverage',
    'nosexcover',
]

setup(
    name='norduniclient',
    version=version,
    url='https://github.com/NORDUnet/python-norduniclient',
    license='Apache License, Version 2.0',
    author='Johan Lundberg',
    author_email='lundberg@nordu.net',
    description='Neo4j (>=3.2.2) database client using bolt for NORDUnet network inventory',
    packages=find_packages(),
    zip_safe=False,
    install_requires=requires,
    tests_require=testing_requires,
    test_suite='nose.collector',
    extras_require={
        'testing': testing_requires
    }
)
