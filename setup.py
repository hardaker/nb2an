import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="nb2an",
    version="1.0",
    author="Wes Hardaker",
    author_email="opensource@hardakers.net",
    description="A set of python scripts to compare or update NetBox and Ansible",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hardaker/nb2an",
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': [
            # migrating to pdb prefixes
            'nb-device = nb2an.tools.getdevice:main',
            'nb-devices = nb2an.tools.getdevices:main',
            'nb-racks = nb2an.tools.getracks:main',
            'nb-outlets = nb2an.tools.getoutlets:main',
            'nb-networks = nb2an.tools.getnetworks:main',
            'nb-check-ansible = nb2an.tools.checkansible:main',
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires = '>=3.6',
)