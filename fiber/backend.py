# Copyright 2020 Uber Technologies, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import os
import importlib
import multiprocessing as mp

import fiber.config as config


_backends = {}
available_backend = ['kubernetes', 'docker', 'local']


def is_inside_kubenetes_job():
    return bool(os.environ.get("KUBERNETES_SERVICE_HOST", None))


def is_inside_docker_job():
    return os.environ.get("FIBER_BACKEND", "") == "docker"


BACKEND_TESTS = {
    "kubernetes": is_inside_kubenetes_job,
    "docker": is_inside_docker_job,
}


def auto_select_backend():
    return next(
        (
            backend_name
            for backend_name, test in BACKEND_TESTS.items()
            if test()
        ),
        config.default_backend,
    )


def get_backend(name=None, **kwargs):
    """
    Returns a working Fiber backend. If `name` is specified, returns a
    backend specified by `name`.
    """
    global _backends
    if name is None:
        name = config.backend if config.backend is not None else auto_select_backend()
    elif name not in available_backend:
        raise mp.ProcessError(f"Invalid backend: {name}")

    _backend = _backends.get(name, None)
    if _backend is None:
        _backend = importlib.import_module(f"fiber.{name}_backend").Backend(**kwargs)
        _backends[name] = _backend
    return _backend
