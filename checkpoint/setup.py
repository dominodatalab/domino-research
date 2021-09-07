import setuptools

setuptools.setup(
    name="checkpoint",
    version="0.1.0",
    author="Kevin Flansburg, Josh Broomberg",
    author_email="kevin.flansburg@dominodatalab.com, josh.broomberg@dominodatalab.com",
    description="Model approval layer for your model registry.",
    url="https://github.com/dominodatalab/domino-research/checkpoint",
    packages=setuptools.find_packages(),
    install_requires=[
        "beautifulsoup4==4.9",
        "Flask==2.0",
        "flask-sqlalchemy==2.5.1",
        "mlflow==1.19",
        "requests==2.26",
    ],
    entry_points={"console_scripts": ["checkpoint = checkpoint.app:main"]},
)
