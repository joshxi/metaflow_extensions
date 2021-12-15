from setuptools import setup, find_packages

setup(
    name="metaflow_extensions",
    use_scm_version=True,
    packages=find_packages(".", exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    include_package_data=True,
    url="",
    license="",
    author="Josh Xi",
    author_email="josh.xi@upstart.com",
    description="Metaflow extension with a custom conda decorator",
    setup_requires=["setuptools_scm"],
    install_requires=["metaflow>=2.4.0"],
    python_requires=">=3.7.0",
)
