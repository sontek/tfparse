#!/usr/bin/env python
# Copyright The Cloud Custodian Authors.
# SPDX-License-Identifier: Apache-2.0
import sys
import sysconfig
import os
from cffi import FFI

here = os.path.dirname(__file__)

def build(setup_kwargs):
    """
    This function is mandatory in order to build the extensions.
    """
    suffix = sysconfig.get_config_var("EXT_SUFFIX")

    libpath = os.path.join(here, f"tfparse{suffix}")
    os.system(
        f"cd gotfparse && go build -buildmode=c-shared  -o {libpath} cmd/tfparse/main.go"
    )
    ffi = FFI()

    ffi.set_source(
        "tfparse._tfparse",
        None,
        include_dirs=[],
        extra_compile_args=["-march=native"],
        libraries=["gotfparse/tfparse.so"],
    )

    ffi.cdef(
        """
            typedef struct {
                char *json;
                char *err;
            } parseResponse;

            parseResponse Parse(char* a, int* e1, int* e2);
            void free(void *ptr);
            """
    )
    ffi.compile()



if __name__ == "__main__":
    build({})
