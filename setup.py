from setuptools import setup, find_packages

VERSION = '0.0.1'

with open('README.md', 'r') as f:
    long_description = f.read()

dependencies = [
    'apscheduler >= 3.0.0',
    'flask >= 1.0.0',
    'flask_socketio >= 4.0.0'
]

setup(
    name='apschedulerui',
    version=VERSION,
    description='',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Federico Schmidt',
    author_email='schmidt.fdr@gmail.com',
    url='https://github.com/schmidtfederico/apscheduler-ui',
    packages=find_packages(exclude=['tests']),
    install_requires=dependencies,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        "Programming Language :: Python :: 3.5",
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Operating System :: OS Independent',
        'Topic :: Internet'
    ],
    python_requires='>=3.5, <4',
    extras_require={
        'testing': ['requests'],
        'testing:python_version == "3.5"': ['mock']
    }
)
