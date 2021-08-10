import setuptools

setuptools.setup(
    name="regsync",
    version="0.1.0",
    author="Kevin Flansburg, Josh Broomberg",
    author_email="kevin.flansburg@dominodatalab.com,josh.broomberg@dominodatalab.com",
    description="Automatically configure serving infrastructure based on model registry.",
    url="https://github.com/dominodatalab/domino-research/regsync",
    packages=setuptools.find_packages(),
    install_requires=[
        "mlflow==1.19",
        "boto3==1.18.*"
    ],
    entry_points={"console_scripts": ["regsync = regsync.app:main"]},
)
