import setuptools
import os

setuptools.setup(
    name="domino-flare",
    version=os.environ.get("RELEASE_VERSION", "SNAPSHOT"),
    author="Kevin Flansburg, Josh Broomberg",
    author_email="kevin.flansburg@dominodatalab.com,josh.broomberg@dominodatalab.com",
    description="Lightweight model monitoring framework.",
    url="https://github.com/dominodatalab/domino-research/flare",
    packages=setuptools.find_packages(),
    install_requires=[
        "dacite==1.6",
        "pandas==1.3.1",
        "numpy==1.21.1",
        "requests==2.26.0",
    ],
)
