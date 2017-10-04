#!/usr/bin/env python
##################################################
# Copyright (C) 2017, All rights reserved.
##################################################

from __future__ import print_function
import argparse

from h1gridlib.artifactory import ArtifactoryItem
from h1gridlib.component_info import ComponentInfo
from h1gridlib.env import EnvDefault

def _main_inner(args):
    component_info = ComponentInfo(
        args.api_key,
        args.base_url,
        args.component_path)

    item = ArtifactoryItem(component_info)
    for f in item.get_folders():
        print(f.paths)

def _main():
    parser = argparse.ArgumentParser(description="h1grid tool")
    parser.add_argument(
        "--base-url",
        metavar="BASEURL",
        default="https://h1grid.com/artifactory",
        help="Artifactory base URL")
    parser.add_argument(
        "--api-key",
        "-k",
        metavar="APIKEY",
        action=EnvDefault,
        env_var="H1GRID_API_KEY",
        help="API key")
    parser.add_argument(
        "component_path",
        metavar="COMPONENTPATH",
        help="Component path")
    args = parser.parse_args()
    _main_inner(args)

if __name__ == "__main__":
    _main()