import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="nb2an",
    version="0.9.11",
    author="Wes Hardaker",
    author_email="opensource@hardakers.net",
    description="A set of python scripts to compare or update NetBox and Ansible",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hardaker/nb2an",
    packages=setuptools.find_packages(),
    entry_points={
        "console_scripts": [
            # migrating to pdb prefixes
            "nb-device = nb2an.tools.getdevice:main",
            "nb-devices = nb2an.tools.getdevices:main",
            "nb-racks = nb2an.tools.getracks:main",
            "nb-outlets = nb2an.tools.getoutlets:main",
            "nb-networks = nb2an.tools.getnetwork:main",
            "nb-update-ansible = nb2an.tools.update_ansible:main",
            "nb-parameters = nb2an.tools.getparameters:main",
            #            'nb-check-ansible = nb2an.tools.checkansible:main',
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "rich",
        "ansible",
        "ruamel.yaml",
        "requests",
        "pyaml",
    ],
    python_requires=">=3.6",
)
