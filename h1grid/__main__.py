##################################################
# Copyright (C) 2017, All rights reserved.
##################################################

from __future__ import print_function
import argparse
import sys

from h1grid import __description__, __project_name__, __version__
from h1grid.artifactory import ArtifactoryRepo
from h1grid.env import EnvDefault

def _dump_folder(folder, depth=0):
    indent = "  " * depth
    print("{}folder: {}".format(indent, folder.api_url))

    for child in folder.files:
        print("{}  file: {}".format(indent, child.api_url))
        print("{}    Download: {}".format(indent, child.download_url))

    for child in folder.folders:
        _dump_folder(child, depth + 1)

def _main_inner(args):
    repo = ArtifactoryRepo(
        args.api_key,
        args.base_url)
    root = repo.fetch(args.path)
    _dump_folder(root)

def _main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument("--version", action="version", version="{} version {}".format(__project_name__, __version__))
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
        "path",
        metavar="PATH",
        help="Object path")

    args = parser.parse_args(argv)
    _main_inner(args)

if __name__ == "__main__":
    _main()
