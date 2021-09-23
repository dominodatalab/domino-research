import setuptools

setuptools.setup(
    name="bridge",
    version="0.1.0",
    python_requires=">=3.9",
    author="Kevin Flansburg, Josh Broomberg",
    author_email="kevin.flansburg@dominodatalab.com,josh.broomberg@dominodatalab.com",
    description="Automatically configure serving infrastructure based on model registry.",
    url="https://github.com/dominodatalab/domino-research/bridge",
    packages=setuptools.find_packages(),
    install_requires=[
        "mlflow==1.19",
        "boto3==1.18.*",
        "requests==2.26",
        "mixpanel==4.9.0",
    ],
    entry_points={"console_scripts": ["bridge = bridge.cli:main"]},
)
