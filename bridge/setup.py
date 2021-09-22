import setuptools

setuptools.setup(
    name="bridge",
    version="0.1.0",
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
        "flask==2.0.1",
        "requests==2.26.0",
        "filelock==3.0.12",
    ],
    entry_points={"console_scripts": ["bridge = bridge.cli:main"]},
)
