import setuptools

setuptools.setup(
    name="monitor",
    version="0.1.0",
    author="Kevin Flansburg, Josh Broomberg",
    author_email="kevin.flansburg@dominodatalab.com,josh.broomberg@dominodatalab.com",
    description="Lightweight model monitoring framework.",
    url="https://github.com/dominodatalab/domino-research/monitor",
    packages=setuptools.find_packages(),
    install_requires=["dacite==1.6", "pandas==1.3.1", "numpy==1.21.1", "requests==2.26.0"],
)
