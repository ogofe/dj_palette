from setuptools import setup, find_packages

setup(
    name="django-palette",
    version="0.1.0",
    description="Build beautiful, component-based Django admin pages with drag-and-drop layouts.",
    author="Joel O. Tanko",
    author_email="7thogofe@email.com",
    url="https://github.com/ogofe/django-palette",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Django>=2.2",
    ],
    classifiers=[
        "Framework :: Django",
        "Programming Language :: Python",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.7",
)
