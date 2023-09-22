from setuptools import setup

with open("README.md", 'r', encoding='utf-8') as f:
    long_description = f.read()

# Setup the app
setup(
    name='src',
    version='0.0.1',
    author='paddy',
    description='A pipeline for recommender system',
    long_description=long_description,
    url='https://github.com/Padmanabhan100/Movie-Recommender-System-Pipeline',
    author_email='paddyrolex10@gmail.com',
    packages=['src'],
    license='GNU',
    python_requires=">=3.6",
    
)