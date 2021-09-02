import setuptools

setuptools.setup(
    name="checkpoint",
    version="0.1.0",
    author="Kevin Flansburg, Josh Broomberg",
    author_email="kevin.flansburg@dominodatalab.com, josh.broomberg@dominodatalab.com",
    description="Model approval layer for your model registry.",
    url="https://github.com/dominodatalab/domino-research/checkpoint",
    packages=setuptools.find_packages(),
    install_requires=[],
    entry_points={"console_scripts": ["checkpoint = checkpoint.app:main"]},
)
