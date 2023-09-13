#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

import argparse
import os
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import List

from setuptools import find_packages, setup

ROOT_DIR = Path(__file__).parent.resolve()


def _get_version():
    try:
        cmd = ["git", "rev-parse", "HEAD"]
        sha = subprocess.check_output(cmd, cwd=str(ROOT_DIR)).decode("ascii").strip()
    except Exception:
        sha = None

    if "BUILD_VERSION" in os.environ:
        version = os.environ["BUILD_VERSION"]
    else:
        with open(os.path.join(ROOT_DIR, "version.txt"), "r") as f:
            version = f.readline().strip()
        if sha is not None:
            version += "+" + sha[:7]

    if sha is None:
        sha = "Unknown"
    return version, sha


def _export_version(version, sha):
    version_path = ROOT_DIR / "torchrec" / "version.py"
    with open(version_path, "w") as fileobj:
        fileobj.write("__version__ = '{}'\n".format(version))
        fileobj.write("git_version = {}\n".format(repr(sha)))


def get_channel():
    # Channel typically takes on the following values:
    # - NIGHTLY: for nightly published binaries
    # - TEST: for binaries build from release candidate branches
    return os.getenv("CHANNEL")


def get_cu_version():
    return os.getenv("CU_VERSION", "cpu")


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="torchrec setup")
    return parser.parse_known_args(argv)


def main(argv: List[str]) -> None:
    args, unknown = parse_args(argv)

    # Set up package version
    channel = get_channel()

    with open(
        os.path.join(os.path.dirname(__file__), "README.MD"), encoding="utf8"
    ) as f:
        readme = f.read()
    with open(
        os.path.join(os.path.dirname(__file__), "install-requirements.txt"),
        encoding="utf8",
    ) as f:
        reqs = f.read()
        install_requires = reqs.strip().split("\n")

    version, sha = _get_version()
    _export_version(version, sha)

    # if channel != "nightly":
    #     if "fbgemm-gpu-nightly" in install_requires:
    #         install_requires.remove("fbgemm-gpu-nightly")
    #     install_requires.append("fbgemm-gpu")

    cu_version = get_cu_version()
    if cu_version == "cpu":
        # if "fbgemm-gpu-nightly" in install_requires:
        #     install_requires.remove("fbgemm-gpu-nightly")
        #     install_requires.append("fbgemm-gpu-nightly-cpu")
        # if "fbgemm-gpu" in install_requires:
            install_requires.remove("fbgemm-gpu")
            install_requires.append("fbgemm-gpu-cpu==0.5.0rc3")
    else:
        install_requires.remove("fbgemm-gpu")
        install_requires.append("fbgemm-gpu==0.5.0rc2")


    print(f"-- torchrec building version: {version} CU Version: {cu_version}")

    packages = find_packages(
        exclude=(
            "*tests",
            "*test",
            "examples",
            "*examples.*",
            "*benchmarks",
            "*build",
            "*rfc",
        )
    )
    sys.argv = [sys.argv[0]] + unknown

    setup(
        # Metadata
        name="torchrec",
        version=version,
        author="TorchRec Team",
        author_email="packages@pytorch.org",
        description="Pytorch domain library for recommendation systems",
        long_description=readme,
        long_description_content_type="text/markdown",
        url="https://github.com/pytorch/torchrec",
        license="BSD-3",
        keywords=["pytorch", "recommendation systems", "sharding"],
        python_requires=">=3.7",
        install_requires=install_requires,
        packages=packages,
        zip_safe=False,
        # PyPI package information.
        classifiers=[
            "Development Status :: 4 - Beta",
            "Intended Audience :: Developers",
            "Intended Audience :: Science/Research",
            "License :: OSI Approved :: BSD License",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.7",
            "Topic :: Scientific/Engineering :: Artificial Intelligence",
        ],
    )


if __name__ == "__main__":
    main(sys.argv[1:])
