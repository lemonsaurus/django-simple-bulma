"""
A small script for publishing releases to GitHub.

This file is designed explicitly with this project in mind - a bunch of values are hardcoded, and it assumes that
you're working with Azure.
"""

import json
import os
import sys

from github import Github
from github.GitRelease import GitRelease
from github.Repository import Repository

MESSAGE = """
**This is an automated release.**

Releases are simply comprised of specific Azure builds. Please see the commit
history for information on the changes.
"""


if len(sys.argv) > 2:
    print("Usage: github-release.py [token]")
    exit(1)

if not os.path.exists("Bot Core/meta/meta.json"):
    print("No such file: Bot Core/meta/meta.json")
    exit(1)


with open("Bot Core/meta/meta.json") as fh:
    metadata = json.load(fh)

sha = metadata["hash"]
tag = metadata["tag"]
token = sys.argv[1]

g = Github("pydis-bot", token)
repo: Repository = g.get_repo("python-discord/pydis-bot-core")

print(f"Creating tag: {tag}")
repo.create_git_ref(f"refs/tags/{tag}", sha)

print(f"Creating release: {tag}")
release: GitRelease = repo.create_git_release(tag, f"Release: {tag}", MESSAGE, target_commitish=sha)

for file in os.listdir("Bot Core/build"):
    print(f"Uploading: {file}")
    release.upload_asset(f"Bot Core/build/{file}")

print("Uploading: doc.zip")
release.upload_asset("Bot Core/documentation/doc.zip")

print(f"Released: {release.html_url}")
