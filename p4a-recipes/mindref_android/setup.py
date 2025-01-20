from setuptools import Extension, find_packages, setup

modules = [
    Extension(
        "mindref.lib.ext.ext",
        sources=["src/mindref/lib/ext/ext.c"],
    )
]


setup(
    name="mindref",
    version="0.1.0",
    description="MindRef",
    package_dir={"": "src"},
    packages=find_packages(where="src", include=["mindref*"]),
    include_package_data=True,
    zip_safe=False,
    install_requires=[],
    data_files=[],
    ext_modules=modules,
)
