from unittest.mock import ANY

import httpx
import pytest
import respx

from syntask.server.api import collections
from syntask.settings import SYNTASK_API_URL

FAKE_DEFAULT_BASE_JOB_TEMPLATE = {
    "job_configuration": {
        "fake": "{{ fake_var }}",
    },
    "variables": {
        "type": "object",
        "properties": {
            "fake_var": {
                "type": "string",
                "default": "fake",
            }
        },
    },
}


@pytest.fixture()
def k8s_default_base_job_template():
    return {
        "job_configuration": {
            "command": "{{ command }}",
            "env": "{{ env }}",
            "labels": "{{ labels }}",
            "name": "{{ name }}",
            "namespace": "{{ namespace }}",
            "job_manifest": {
                "apiVersion": "batch/v1",
                "kind": "Job",
                "metadata": {
                    "labels": "{{ labels }}",
                    "namespace": "{{ namespace }}",
                    "generateName": "{{ name }}-",
                },
                "spec": {
                    "backoffLimit": 0,
                    "ttlSecondsAfterFinished": "{{ finished_job_ttl }}",
                    "template": {
                        "spec": {
                            "parallelism": 1,
                            "completions": 1,
                            "restartPolicy": "Never",
                            "serviceAccountName": "{{ service_account_name }}",
                            "containers": [
                                {
                                    "name": "syntask-job",
                                    "env": "{{ env }}",
                                    "image": "{{ image }}",
                                    "imagePullPolicy": "{{ image_pull_policy }}",
                                    "args": "{{ command }}",
                                }
                            ],
                        }
                    },
                },
            },
            "cluster_config": "{{ cluster_config }}",
            "job_watch_timeout_seconds": "{{ job_watch_timeout_seconds }}",
            "pod_watch_timeout_seconds": "{{ pod_watch_timeout_seconds }}",
            "stream_output": "{{ stream_output }}",
        },
        "variables": {
            "description": (
                "Default variables for the Kubernetes worker.\n\nThe schema for this"
                " class is used to populate the `variables` section of the"
                " default\nbase job template."
            ),
            "type": "object",
            "properties": {
                "name": {
                    "title": "Name",
                    "description": "Name given to infrastructure created by a worker.",
                    "type": "string",
                },
                "env": {
                    "title": "Environment Variables",
                    "description": (
                        "Environment variables to set when starting a flow run."
                    ),
                    "type": "object",
                    "additionalProperties": {"type": "string"},
                },
                "labels": {
                    "title": "Labels",
                    "description": (
                        "Labels applied to infrastructure created by a worker."
                    ),
                    "type": "object",
                    "additionalProperties": {"type": "string"},
                },
                "command": {
                    "title": "Command",
                    "description": (
                        "The command to use when starting a flow run. In most cases,"
                        " this should be left blank and the command will be"
                        " automatically generated by the worker."
                    ),
                    "type": "string",
                },
                "namespace": {
                    "title": "Namespace",
                    "description": "The Kubernetes namespace to create jobs within.",
                    "default": "default",
                    "type": "string",
                },
                "image": {
                    "title": "Image",
                    "description": (
                        "The image reference of a container image to use for created"
                        " jobs. If not set, the latest Syntask image will be used."
                    ),
                    "example": "docker.io/synopkg/syntask:3-latest",
                    "type": "string",
                },
                "service_account_name": {
                    "title": "Service Account Name",
                    "description": (
                        "The Kubernetes service account to use for job creation."
                    ),
                    "type": "string",
                },
                "image_pull_policy": {
                    "title": "Image Pull Policy",
                    "description": (
                        "The Kubernetes image pull policy to use for job containers."
                    ),
                    "default": "IfNotPresent",
                    "enum": ["IfNotPresent", "Always", "Never"],
                    "type": "string",
                },
                "finished_job_ttl": {
                    "title": "Finished Job TTL",
                    "description": (
                        "The number of seconds to retain jobs after completion. If set,"
                        " finished jobs will be cleaned up by Kubernetes after the"
                        " given delay. If not set, jobs will be retained indefinitely."
                    ),
                    "type": "integer",
                },
                "job_watch_timeout_seconds": {
                    "title": "Job Watch Timeout Seconds",
                    "description": (
                        "Number of seconds to wait for each event emitted by a job"
                        " before timing out. If not set, the worker will wait for each"
                        " event indefinitely."
                    ),
                    "type": "integer",
                },
                "pod_watch_timeout_seconds": {
                    "title": "Pod Watch Timeout Seconds",
                    "description": (
                        "Number of seconds to watch for pod creation before timing out."
                    ),
                    "default": 60,
                    "type": "integer",
                },
                "stream_output": {
                    "title": "Stream Output",
                    "description": (
                        "If set, output will be streamed from the job to local standard"
                        " output."
                    ),
                    "default": True,
                    "type": "boolean",
                },
                "cluster_config": {
                    "title": "Cluster Config",
                    "description": (
                        "The Kubernetes cluster config to use for job creation."
                    ),
                    "allOf": [{"$ref": "#/definitions/KubernetesClusterConfig"}],
                },
            },
            "definitions": {
                "KubernetesClusterConfig": {
                    "title": "KubernetesClusterConfig",
                    "description": (
                        "Stores configuration for interaction with Kubernetes"
                        " clusters.\n\nSee `from_file` for creation."
                    ),
                    "type": "object",
                    "properties": {
                        "config": {
                            "title": "Config",
                            "description": (
                                "The entire contents of a kubectl config file."
                            ),
                            "type": "object",
                        },
                        "context_name": {
                            "title": "Context Name",
                            "description": "The name of the kubectl context to use.",
                            "type": "string",
                        },
                    },
                    "required": ["config", "context_name"],
                    "block_type_slug": "kubernetes-cluster-config",
                    "secret_fields": [],
                    "block_schema_references": {},
                }
            },
        },
    }


@pytest.fixture()
def docker_default_base_job_template():
    return {
        "job_configuration": {
            "command": "{{ command }}",
            "env": "{{ env }}",
            "labels": "{{ labels }}",
            "name": "{{ name }}",
            "image": "{{ image }}",
            "image_pull_policy": "{{ image_pull_policy }}",
            "networks": "{{ networks }}",
            "network_mode": "{{ network_mode }}",
            "auto_remove": "{{ auto_remove }}",
            "volumes": "{{ volumes }}",
            "stream_output": "{{ stream_output }}",
            "mem_limit": "{{ mem_limit }}",
            "memswap_limit": "{{ memswap_limit }}",
            "privileged": "{{ privileged }}",
        },
        "variables": {
            "description": (
                "Configuration class used by the Docker worker.\n\nAn instance of this"
                " class is passed to the Docker worker's `run` method\nfor each flow"
                " run. It contains all the information necessary to execute the\nflow"
                " run as a Docker container.\n\nAttributes:\n    name: The name to give"
                " to created Docker containers.\n    command: The command executed in"
                " created Docker containers to kick off\n        flow run execution.\n "
                "   env: The environment variables to set in created Docker"
                " containers.\n    labels: The labels to set on created Docker"
                " containers.\n    image: The image reference of a container image to"
                " use for created jobs.\n        If not set, the latest Syntask image"
                " will be used.\n    image_pull_policy: The image pull policy to use"
                " when pulling images.\n    networks: Docker networks that created"
                " containers should be connected to.\n    network_mode: The network"
                " mode for the created containers (e.g. host, bridge).\n        If"
                " 'networks' is set, this cannot be set.\n    auto_remove: If set,"
                " containers will be deleted on completion.\n    volumes: Docker"
                " volumes that should be mounted in created containers.\n   "
                " stream_output: If set, the output from created containers will be"
                " streamed\n        to local standard output.\n    mem_limit: Memory"
                " limit of created containers. Accepts a value\n        with a unit"
                " identifier (e.g. 100000b, 1000k, 128m, 1g.) If a value is\n       "
                " given without a unit, bytes are assumed.\n    memswap_limit: Total"
                " memory (memory + swap), -1 to disable swap. Should only be\n       "
                " set if `mem_limit` is also set. If `mem_limit` is set, this defaults"
                " to\n        allowing the container to use as much swap as memory. For"
                " example, if\n        `mem_limit` is 300m and `memswap_limit` is not"
                " set, containers can use\n        600m in total of memory and swap.\n "
                "   privileged: Give extended privileges to created containers."
            ),
            "type": "object",
            "properties": {
                "command": {
                    "title": "Command",
                    "description": (
                        "The command to use when starting a flow run. In most cases,"
                        " this should be left blank and the command will be"
                        " automatically generated by the worker."
                    ),
                    "type": "string",
                },
                "env": {
                    "title": "Environment Variables",
                    "description": (
                        "Environment variables to set when starting a flow run."
                    ),
                    "type": "object",
                    "additionalProperties": {"type": "string"},
                },
                "labels": {
                    "title": "Labels",
                    "description": (
                        "Labels applied to infrastructure created by the worker using"
                        " this job configuration."
                    ),
                    "type": "object",
                    "additionalProperties": {"type": "string"},
                },
                "name": {
                    "title": "Name",
                    "description": (
                        "Name given to infrastructure created by the worker using this"
                        " job configuration."
                    ),
                    "type": "string",
                },
                "image": {
                    "title": "Image",
                    "description": (
                        "The image reference of a container image to use for created"
                        " jobs. If not set, the latest Syntask image will be used."
                    ),
                    "example": "docker.io/synopkg/syntask:3-latest",
                    "type": "string",
                },
                "image_pull_policy": {
                    "title": "Image Pull Policy",
                    "description": "The image pull policy to use when pulling images.",
                    "enum": ["IfNotPresent", "Always", "Never"],
                    "type": "string",
                },
                "networks": {
                    "title": "Networks",
                    "description": (
                        "Docker networks that created containers should be"
                        " connected to."
                    ),
                    "type": "array",
                    "items": {"type": "string"},
                },
                "network_mode": {
                    "title": "Network Mode",
                    "description": (
                        "The network mode for the created containers (e.g. host,"
                        " bridge). If 'networks' is set, this cannot be set."
                    ),
                    "type": "string",
                },
                "auto_remove": {
                    "title": "Auto Remove",
                    "description": "If set, containers will be deleted on completion.",
                    "default": False,
                    "type": "boolean",
                },
                "volumes": {
                    "title": "Volumes",
                    "description": "A list of volume to mount into created containers.",
                    "example": ["/my/local/path:/path/in/container"],
                    "type": "array",
                    "items": {"type": "string"},
                },
                "stream_output": {
                    "title": "Stream Output",
                    "description": (
                        "If set, the output from created containers will be streamed to"
                        " local standard output."
                    ),
                    "default": True,
                    "type": "boolean",
                },
                "mem_limit": {
                    "title": "Memory Limit",
                    "description": (
                        "Memory limit of created containers. Accepts a value with a"
                        " unit identifier (e.g. 100000b, 1000k, 128m, 1g.) If a value"
                        " is given without a unit, bytes are assumed."
                    ),
                    "type": "string",
                },
                "memswap_limit": {
                    "title": "Memory Swap Limit",
                    "description": (
                        "Total memory (memory + swap), -1 to disable swap. Should only"
                        " be set if `mem_limit` is also set. If `mem_limit` is set,"
                        " this defaults toallowing the container to use as much swap as"
                        " memory. For example, if `mem_limit` is 300m and"
                        " `memswap_limit` is not set, containers can use 600m in total"
                        " of memory and swap."
                    ),
                    "type": "string",
                },
                "privileged": {
                    "title": "Privileged",
                    "description": "Give extended privileges to created container.",
                    "default": False,
                    "type": "boolean",
                },
            },
        },
    }


@pytest.fixture(autouse=True)
def cleared_collection_registry_cache():
    collections.GLOBAL_COLLECTIONS_VIEW_CACHE.clear()
    yield
    collections.GLOBAL_COLLECTIONS_VIEW_CACHE.clear()


@pytest.fixture()
def mock_collection_registry(
    docker_default_base_job_template,
    k8s_default_base_job_template,
):
    mock_body = {
        "syntask-fake": {
            "fake": {
                "type": "fake",
                "default_base_job_configuration": FAKE_DEFAULT_BASE_JOB_TEMPLATE,
                "display_name": "Syntask Fake",
                "description": "A Syntask Fake pool.",
            }
        },
        "syntask-cloud": {
            "syntask-cloud:push": {
                "type": "cloud-run:push",
                "default_base_job_configuration": {},
                "is_push_pool": True,
                "display_name": "Syntask Cloud Run: Push",
                "description": "A Syntask Cloud Run: Push pool.",
            }
        },
        "prefect-docker": {
            "docker": {
                "type": "docker",
                "default_base_job_configuration": docker_default_base_job_template,
            }
        },
        "syntask-kubernetes": {
            "kubernetes": {
                "type": "kubernetes",
                "default_base_job_configuration": k8s_default_base_job_template,
            }
        },
    }

    with respx.mock(
        assert_all_mocked=False,
        assert_all_called=False,
        base_url=SYNTASK_API_URL.value(),
    ) as respx_mock:
        respx_mock.get("/csrf-token", params={"client": ANY}).pass_through()
        respx_mock.route(path__startswith="/work_pools/").pass_through()
        respx_mock.get("/collections/views/aggregate-worker-metadata").mock(
            return_value=httpx.Response(200, json=mock_body)
        )
        yield
