"""
A small script for saving version information to `meta.json`.

This is intended to be used as part of a larger toolchain - it exists because
we need to publish a build artifact when working with Azure, in order to tag
releases automatically.
"""

import json
import subprocess

git_hash = subprocess.check_output(
    ("git", "rev-parse", "--long", "HEAD")
).decode("UTF-8").split("\n")[1]

package_version = subprocess.check_output(
    ("python", "setup.py", "--version")
).decode("UTF-8").strip("\n")


data = {
    "tag": package_version,
    "hash": git_hash
}


with open("meta.json", "w") as fh:
    json.dump(data, fh)

print(f"meta.json written: {package_version} ({git_hash})")
