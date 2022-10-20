#!/usr/bin/env python
# Copyright The Cloud Custodian Authors.
# SPDX-License-Identifier: Apache-2.0
import os
import sys
import platform
from distutils.command.build_ext import build_ext
from distutils.errors import CCompilerError, DistutilsExecError, DistutilsPlatformError
from distutils.extension import Extension

ext_modules = [Extension("tfparse", ["gotfparse/cmd/tfparse/main.go"])]
cffi_modules = ["tfparse/build_cffi.py:ffi"]
build_golang = {"root": "github.com/cloud-custodian/tfparse/gotfparse"}


class BuildFailed(Exception):
    pass


class ExtBuilder(build_ext):
    def run(self):
        try:
            build_ext.run(self)
        except (DistutilsPlatformError, FileNotFoundError):
            raise BuildFailed("File not found. Could not compile C extension.")

    def build_extension(self, ext):
        try:
            build_ext.build_extension(self, ext)
        except (CCompilerError, DistutilsExecError, DistutilsPlatformError, ValueError):
            raise BuildFailed("Could not compile C extension.")


def build(setup_kwargs):
    """
    This function is mandatory in order to build the extensions.
    """
    setup_kwargs.update(
        {
            "build_golang": build_golang,
            "ext_modules": ext_modules,
            "cffi_modules": cffi_modules,
            "cmdclass": {"build_ext": ExtBuilder},
        }
    )
    if sys.platform == "darwin" and os.getenv("_PYTHON_HOST_PLATFORM"):
        # Currently poetry lacks a few features we need to create platform
        # specific wheels.  So we are overriding that here for OSX since it
        # currently needs to be cross-compiled using
        # - _PYTHON_HOST_PLATFORM
        # - ARCHFLAGS
        # https://github.com/python-poetry/poetry/issues/2051
        # https://github.com/python-poetry/poetry/issues/2613
        release = platform.mac_ver()[0]
        machine = platform.machine()
        host_platform = os.getenv("_PYTHON_HOST_PLATFORM")
        go_arch = os.getenv("GOARCH")
        arch_flags = os.getenv("ARCHFLAGS")

        # If the MACOSX_DEPLOYMENT_TARGET environment variable is defined, use
        # it, as it will be the most accurate. Otherwise use the value returned by
        # platform.mac_ver() provided by the platform module available in the
        # Python standard library.
        #
        # Note that on macOS, distutils.util.get_platform() is not used because
        # it returns the macOS version on which Python was built which may be
        # significantly older than the user's current machine.
        release = os.environ.get("MACOSX_DEPLOYMENT_TARGET", release)
        major_macos, minor_macos = release.split(".")[:2]

        # On macOS 11+, only the major version matters.
        if int(major_macos) >= 11:
            minor_macos = "0"

        print("========= Release Info =========")
        print(f"{release=}")
        print(f"{machine=}")
        print(f"{host_platform=}")
        print(f"{go_arch=}")
        print(f"{arch_flags=}")
        print("================================")

        platform_name = f"macosx-{major_macos}.{minor_macos}-{machine}"

        setup_kwargs.update(
            {
                "script_args": ["bdist_wheel"],
                "options": {
                    "bdist_wheel": {
                        "plat_name": platform_name,
                    },
                    "egg_info": {"egg_base": "./build/"},
                },
            }
        )


if __name__ == "__main__":
    build({})
