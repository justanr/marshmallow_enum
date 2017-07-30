from setuptools import setup

try:
    import enum  # noqa
    extra_requires = []
except ImportError:
    extra_requires = ['enum34']

REQUIRES = ['marshmallow>=2.0.0'] + extra_requires


if __name__ == '__main__':
    setup(
        name='marshmallow-enum',
        version='1.3',
        author='Alec Nikolas Reiter',
        author_email='alecreiter@gmail.com',
        description='Enum field for Marshmallow',
        license='MIT',
        packages=['marshmallow_enum'],
        install_requires=REQUIRES,
    )
