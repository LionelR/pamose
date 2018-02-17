from setuptools import setup, find_packages

setup(
    name='pamose',
    version='1.0',
    long_description=__doc__,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'click',
        'werkzeug',
        'flask',
        'flask-restful',
        'sqlalchemy',
        'marshmallow-sqlalchemy',
        'flask-sqlalchemy',
        'flask_marshmallow',
        'pytest'
    ],
    entry_points='''
        [console_scripts]
        pamose=pamose.launcher:cli
    ''',
)
