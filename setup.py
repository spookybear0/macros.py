# template from nekitdev on github

from setuptools import setup
from pathlib import Path
import re
import site

__version__ = "0.1.0"

for site_packages_path in reversed(site.getsitepackages()):
    site_packages = Path(site_packages_path)

    if site_packages.exists():
        break

else:
    site_packages = Path(site.USER_SITE)

try:
    (site_packages / "macros.pth").touch()  # attempt to create the path file
except OSError:
    site_packages = Path(site.USER_SITE)

root = Path(__file__).parent

requirements = (root / "requirements.txt").read_text("utf-8").splitlines()

version = __version__

long_description = (root / "README.md").read_text("utf-8")

# copy path file from the root directory into site packages
(site_packages / "macros.pth").write_text((root / "macros.pth").read_text("utf-8"), "utf-8")

setup(
    name="macros.py",
    author="spookybear0",
    author_email="collinmcarroll@gmail.com",
    url="https://github.com/spookybear0/macros.py",
    project_urls={
        "Issue tracker": "https://github.com/spookybear0/macros.py/issues"
    },
    version=version,
    packages=["macros"],
    license="MIT",
    description="Macros for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    include_package_data=True,
    install_requires=requirements,
    python_requires=">=3.5",
)