##################################################
# Copyright (C) 2017, All rights reserved.
##################################################

from pyprelude.util import unpack_args

_API_STORAGE_PATH = "api/storage"

class ComponentInfo(object):
    def __init__(self, api_key, artifactory_url, real_component_path, virtual_component_path=None):
        self._api_key = api_key
        self._artifactory_url = artifactory_url.strip("/")
        self._real_component_path = real_component_path.strip("/")
        temp = real_component_path if virtual_component_path is None else virtual_component_path
        self._virtual_component_path = temp.strip("/")

    @property
    def api_key(self): return self._api_key

    def real_api_url(self, *args):
        return self._api_url(self._real_component_path, *args)

    def virtual_api_url(self, *args):
        return self._api_url(self._virtual_component_path, *args)

    def download_url(self, *args):
        paths = map(lambda x: x.strip("/"), unpack_args(*args))
        result = "/".join([self._artifactory_url, self._virtual_component_path] + paths)
        return result

    def _api_url(self, component_path, *args):
        paths = map(lambda x: x.strip("/"), unpack_args(*args))
        result = "/".join([self._artifactory_url, _API_STORAGE_PATH, component_path] + paths)
        return result
