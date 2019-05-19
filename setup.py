import setuptools

with open("README.md", 'r') as readme:
    setuptools.setup(
        name = 'openmemobird',
        version = '1.0.0a3',
        author = "LeMinaw",
        author_email = "le@minaw.net",
        description = "Package to send data and documents to Memobird printers.",
        long_description = readme.read(),
        long_description_content_type = "text/markdown",
        url = "https://github.com/leminaw/openmemobird",
        packages = setuptools.find_packages(),
        install_requires = [
            'requests>=2.0.0',
            'Pillow>=5.0.0'
        ],
        classifiers = [
            'Programming Language :: Python :: 3',
            'Development Status :: 3 - Alpha',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
        ],
    )
