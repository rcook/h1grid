#!/usr/bin/env python
##################################################
# Copyright (C) 2017, All rights reserved.
##################################################

from __future__ import print_function
import argparse

from h1gridlib.env import EnvDefault

def _main_inner(args):
    print("Hello from h1grid")
    print(args)

def _main():
    parser = argparse.ArgumentParser(description="h1grid tool")
    parser.add_argument(
        "--api-key",
        "-k",
        metavar="APIKEY",
        action=EnvDefault,
        env_var="H1GRID_API_KEY",
        help="API key")
    args = parser.parse_args()
    _main_inner(args)

if __name__ == "__main__":
    _main()