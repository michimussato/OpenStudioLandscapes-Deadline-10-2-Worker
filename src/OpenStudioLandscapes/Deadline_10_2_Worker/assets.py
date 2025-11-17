import copy
import json
import pathlib
import shlex
import shutil
import textwrap
import time
import urllib.parse
from typing import Any, Generator

import yaml
from dagster import (
    AssetExecutionContext,
    AssetIn,
    AssetKey,
    AssetMaterialization,
    MetadataValue,
    Output,
    asset,
)
from OpenStudioLandscapes.engine.common_assets.compose import get_compose
from OpenStudioLandscapes.engine.common_assets.constants import get_constants
from OpenStudioLandscapes.engine.common_assets.docker_compose_graph import (
    get_docker_compose_graph,
)
from OpenStudioLandscapes.engine.common_assets.docker_config import get_docker_config
from OpenStudioLandscapes.engine.common_assets.docker_config_json import (
    get_docker_config_json,
)
from OpenStudioLandscapes.engine.common_assets.env import get_env
from OpenStudioLandscapes.engine.common_assets.feature_out import get_feature_out
from OpenStudioLandscapes.engine.common_assets.group_in import get_group_in
from OpenStudioLandscapes.engine.common_assets.group_out import get_group_out
from OpenStudioLandscapes.engine.constants import *
from OpenStudioLandscapes.engine.enums import *
from OpenStudioLandscapes.engine.utils import *
from OpenStudioLandscapes.engine.utils.docker import *

from OpenStudioLandscapes.Deadline_10_2_Worker.constants import *

constants = get_constants(
    ASSET_HEADER=ASSET_HEADER,
)


docker_config = get_docker_config(
    ASSET_HEADER=ASSET_HEADER,
)


group_in = get_group_in(
    ASSET_HEADER=ASSET_HEADER,
    ASSET_HEADER_PARENT=ASSET_HEADER_PARENT,
    input_name=str(GroupIn.FEATURE_IN),
)


env = get_env(
    ASSET_HEADER=ASSET_HEADER,
)


group_out = get_group_out(
    ASSET_HEADER=ASSET_HEADER,
)


docker_compose_graph = get_docker_compose_graph(
    ASSET_HEADER=ASSET_HEADER,
)


compose = get_compose(
    ASSET_HEADER=ASSET_HEADER,
)


feature_out = get_feature_out(
    ASSET_HEADER=ASSET_HEADER,
    feature_out_ins={
        "env": dict,
        "compose": dict,
        "group_in": dict,
        "deadline_command_compose_worker_runner": list,
        "deadline_command_compose_pulse_runner": list,
    },
)


docker_config_json = get_docker_config_json(
    ASSET_HEADER=ASSET_HEADER,
)


@asset(
    **ASSET_HEADER,
    ins={
        "env": AssetIn(
            AssetKey([*ASSET_HEADER["key_prefix"], "env"]),
        ),
        "docker_config_json": AssetIn(
            AssetKey([*ASSET_HEADER["key_prefix"], "docker_config_json"]),
        ),
        "docker_config": AssetIn(
            AssetKey([*ASSET_HEADER["key_prefix"], "docker_config"])
        ),
        # "group_in": AssetIn(
        #     AssetKey([*ASSET_HEADER_BASE["key_prefix"], str(GroupIn.BASE_IN)])
        # ),
        # Todo:
        #  - [ ] this dependency should be coming from AssetKey([*ASSET_HEADER["key_prefix"], "group_in"])
        "build_docker_image_stem": AssetIn(
            AssetKey([*ASSET_HEADER_PARENT["key_prefix"], "build_docker_image"]),
        ),
        # Todo:
        #  - [ ] this dependency should be coming from AssetKey([*ASSET_HEADER["key_prefix"], "group_in"])
        "deadline_command_build_client_image_10_2": AssetIn(
            AssetKey(
                [
                    *ASSET_HEADER_PARENT["key_prefix"],
                    "deadline_command_build_docker_image_client",
                ]
            ),
        ),
    },
)
def build_docker_image_client(
    context: AssetExecutionContext,
    env: dict,  # pylint: disable=redefined-outer-name
    docker_config_json: pathlib.Path,  # pylint: disable=redefined-outer-name
    docker_config: DockerConfig,  # pylint: disable=redefined-outer-name
    # group_in: dict,  # pylint: disable=redefined-outer-name
    build_docker_image_stem: dict,  # pylint: disable=redefined-outer-name
    deadline_command_build_client_image_10_2: list,  # pylint: disable=redefined-outer-name
) -> Generator[Output[dict] | AssetMaterialization, None, None]:
    """ """

    # docker_image: dict = group_in["docker_image"]

    # Todo:
    #  - [ ] Create dynamic yet persistent hostname so that we can use THE SAME
    #        docker-compose file on an arbitrary number of hosts without conflicts
    #        - https://forums.docker.com/t/change-hostname-of-an-existing-container/361/16
    #          `docker inspect -f '{{ .State.Pid }}' deadline-10-2-worker-001`
    #          `sudo nsenter --target 400453 --uts`
    #          One line (enter ns): `sudo nsenter --target $(docker inspect -f '{{ .State.Pid }}' deadline-10-2-worker-001) --uts`
    #          One line (run command): `sudo nsenter --target $(docker inspect -f '{{ .State.Pid }}' deadline-10-2-worker-001) --uts hostname "new-hostname"`
    #          One line (run command): `sudo nsenter --target $(docker inspect -f '{{ .State.Pid }}' deadline-10-2-worker-001) --uts hostname "$(hostname)-new-hostname"`

    docker_file = pathlib.Path(
        env["DOT_LANDSCAPES"],
        env.get("LANDSCAPE", "default"),
        f"{ASSET_HEADER['group_name']}__{'__'.join(ASSET_HEADER['key_prefix'])}",
        "__".join(context.asset_key.path),
        "Dockerfiles",
        "Dockerfile",
    )

    docker_file.parent.mkdir(parents=True, exist_ok=True)

    #################################################

    (
        image_name,
        image_prefixes,
        tags,
        build_base_parent_image_prefix,
        build_base_parent_image_name,
        build_base_parent_image_tags
    ) = get_image_metadata(
        context=context,
        docker_image=build_docker_image_stem,
        docker_config=docker_config,
        env=env,
    )

    #################################################

    # @formatter:off
    docker_file_str = textwrap.dedent(
        """\
        # {auto_generated}
        # {dagster_url}
        FROM {parent_image} AS {image_name}
        LABEL authors="{AUTHOR}"

        SHELL ["/bin/bash", "-c"]

        WORKDIR /installers

        RUN {deadline_command}

        WORKDIR /opt/Thinkbox

        ENTRYPOINT []
        """
    ).format(
        auto_generated=f"AUTO-GENERATED by Dagster Asset {'__'.join(context.asset_key.path)}",
        dagster_url=urllib.parse.quote(
            f"http://localhost:3000/asset-groups/{'%2F'.join(context.asset_key.path)}",
            safe=":/%",
        ),
        image_name=image_name,
        # Todo: this won't work as expected if len(tags) > 1
        parent_image=f"{build_base_parent_image_prefix}{build_base_parent_image_name}:{build_base_parent_image_tags[0]}",
        deadline_command=" ".join(
            shlex.quote(s) for s in deadline_command_build_client_image_10_2
        ),
        **env,
    )
    # @formatter:on

    # shutil.rmtree(docker_file.parent, ignore_errors=True)
    #
    # docker_file.parent.mkdir(parents=True, exist_ok=True)

    with open(docker_file, "w") as fw:
        fw.write(docker_file_str)

    with open(docker_file, "r") as fr:
        docker_file_content = fr.read()

    #################################################

    image_data, logs = create_image(
        context=context,
        image_name=image_name,
        image_prefixes=image_prefixes,
        tags=tags,
        docker_image=build_docker_image_stem,
        docker_config=docker_config,
        docker_config_json=docker_config_json,
        docker_file=docker_file,
    )

    yield Output(image_data)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(image_data),
            "docker_file": MetadataValue.md(f"```shell\n{docker_file_content}\n```"),
            "env": MetadataValue.json(env),
            "logs": MetadataValue.json(logs),
        },
    )


@asset(
    **ASSET_HEADER,
    ins={
        "env": AssetIn(
            AssetKey([*ASSET_HEADER["key_prefix"], "env"]),
        ),
    },
)
def deadline_ini(
    context: AssetExecutionContext,
    env: dict,  # pylint: disable=redefined-outer-name
    # Todo:
) -> Generator[Output[pathlib.Path] | AssetMaterialization, None, None]:
    # @formatter:off
    deadline_ini = textwrap.dedent(
        """\
        # {auto_generated}
        # {dagster_url}
        # Full Documentation
        # https://docs.thinkboxsoftware.com/products/deadline/10.2/1_User%20Manual/manual/client-config.html#client-config-conn-server-ref-label
        [Deadline]
        # For Remote
        ConnectionType=Remote
        ProxyRoot={rcs_runner_hostname}:{RCS_HTTP_PORT_HOST}
        ProxyRoot0={rcs_runner_hostname}:{RCS_HTTP_PORT_HOST}
        ###
        # #################################
        # # For Repository
        # ConnectionType=Repository
        # NetworkRoot=/opt/Thinkbox/DeadlineRepository10
        # NetworkRoot0=/opt/Thinkbox/DeadlineRepository10
        ###
        WebServiceHttpListenPort={WEBSERVICE_HTTP_PORT_HOST}
        WebServiceTlsListenPort=0
        WebServiceTlsServerCert=
        WebServiceTlsCaCert=
        WebServiceTlsAuth=False
        WebServiceClientSSLAuthentication=NotRequired
        HttpListenPort={RCS_HTTP_PORT_HOST}
        TlsListenPort=0
        LicenseMode=LicenseFree
        Region=
        LauncherListeningPort=17000
        LauncherServiceStartupDelay=60
        AutoConfigurationPort=17001
        SlaveStartupPort=17003
        LicenseForwarderListeningPort=17004
        SlaveDataRoot=
        NoGuiMode=false
        AutoUpdateOverride=false
        IncludeRCSInLauncherMenu=true
        DbSSLCertificate=
        AutoUpdateBlock=NotBlocked

        # Controlled by Docker
        LaunchRemoteConnectionServerAtStartup=false
        KeepRemoteConnectionServerRunning=false
        LaunchPulseAtStartup=false
        KeepPulseRunning=false
        LaunchBalancerAtStartup=false
        KeepBalancerRunning=false
        KeepWebServiceRunning=false
        KeepWorkerRunning=false
        RestartStalledSlave=false
        LaunchLicenseForwarderAtStartup=false
        KeepLicenseForwarderRunning=false
        LaunchSlaveAtStartup=false
        """
    ).format(
        auto_generated=f"AUTO-GENERATED by Dagster Asset {'__'.join(context.asset_key.path)}",
        dagster_url=urllib.parse.quote(
            f"http://localhost:3000/asset-groups/{'%2F'.join(context.asset_key.path)}",
            safe=":/%",
        ),
        rcs_runner_hostname=".".join(
            ["deadline-rcs-runner-10-2", env["OPENSTUDIOLANDSCAPES__DOMAIN_LAN"]]
        ),
        **env,
    )
    # @formatter:on

    deadline_client_ini = pathlib.Path(
        env["DOT_LANDSCAPES"],
        env.get("LANDSCAPE", "default"),
        f"{ASSET_HEADER['group_name']}__{'__'.join(ASSET_HEADER['key_prefix'])}",
        "configs",
        "Deadline10",
        "deadline.ini",
    ).expanduser()

    deadline_client_ini.parent.mkdir(parents=True, exist_ok=True)

    with open(deadline_client_ini, "w") as fw:
        fw.write(deadline_ini)

    yield Output(deadline_client_ini)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.path(deadline_client_ini),
            "deadline_ini": MetadataValue.md(f"```\n{deadline_ini}\n```"),
            "env": MetadataValue.json(env),
        },
    )


@asset(
    **ASSET_HEADER,
    ins={
        "env": AssetIn(
            AssetKey([*ASSET_HEADER["key_prefix"], "env"]),
        ),
        "build": AssetIn(
            AssetKey([*ASSET_HEADER["key_prefix"], "build_docker_image_client"]),
        ),
        "deadline_ini_10_2": AssetIn(
            AssetKey([*ASSET_HEADER["key_prefix"], "deadline_ini"]),
        ),
        "deadline_command_compose_pulse_runner_10_2": AssetIn(
            AssetKey(
                [*ASSET_HEADER["key_prefix"], "deadline_command_compose_pulse_runner"]
            ),
        ),
        "compose_networks_10_2": AssetIn(
            AssetKey([*ASSET_HEADER["key_prefix"], "compose_networks"]),
        ),
    },
)
def compose_pulse_runner(
    context: AssetExecutionContext,
    env: dict,  # pylint: disable=redefined-outer-name
    build: dict,  # pylint: disable=redefined-outer-name
    deadline_ini_10_2: pathlib.Path,  # pylint: disable=redefined-outer-name
    deadline_command_compose_pulse_runner_10_2: list,  # pylint: disable=redefined-outer-name
    compose_networks_10_2: dict,  # pylint: disable=redefined-outer-name
) -> Generator[Output[dict[str, dict[str, dict]]] | AssetMaterialization, None, None]:
    """ """

    network_dict = {}
    ports_dict = {}

    if "networks" in compose_networks_10_2:
        network_dict = {
            "networks": list(compose_networks_10_2.get("networks", {}).keys())
        }
        ports_dict = {
            "ports": [
                f"{env['DAGSTER_DEV_PORT_HOST']}:{env['DAGSTER_DEV_PORT_CONTAINER']}",
            ]
        }
    elif "network_mode" in compose_networks_10_2:
        network_dict = {"network_mode": compose_networks_10_2["network_mode"]}

    volumes_dict = {
        "volumes": [
            f"{deadline_ini_10_2.as_posix()}:/var/lib/Thinkbox/Deadline10/deadline.ini:ro",
            f"{env['REPOSITORY_INSTALL_DESTINATION_%s' % '__'.join(ASSET_HEADER_PARENT['key_prefix'])]}:/opt/Thinkbox/DeadlineRepository10",
        ]
    }

    # For portability, convert absolute volume paths to relative paths

    _volume_relative = []

    for v in volumes_dict["volumes"]:

        host, container = v.split(":", maxsplit=1)

        volume_dir_host_rel_path = get_relative_path_via_common_root(
            context=context,
            path_src=pathlib.Path(env["DOCKER_COMPOSE"]),
            path_dst=pathlib.Path(host),
            path_common_root=pathlib.Path(env["DOT_LANDSCAPES"]),
        )

        _volume_relative.append(
            f"{volume_dir_host_rel_path.as_posix()}:{container}",
        )

    volumes_dict = {
        "volumes": [
            *_volume_relative,
        ]
    }

    service_name_base = "deadline-10-2-pulse-worker"
    padding = 3

    docker_dict = {"services": {}}

    for i in range(NUM_SERVICES):
        service_name = f"{service_name_base}-{str(i+1).zfill(padding)}"
        container_name = "--".join([service_name, env.get("LANDSCAPE", "default")])
        # host_name = ".".join([env["HOSTNAME_PULSE_RUNNER"] or service_name, env["OPENSTUDIOLANDSCAPES__DOMAIN_LAN"]])

        # # deadlinepulse does not have a -name flag
        # deadline_command_compose_pulse_runner_10_2.extend(
        #     [
        #         "-name",
        #         str(service_name)
        #     ]
        # )

        service = {
            "container_name": container_name,
            # To have a unique, dynamic hostname, we simply must not
            # specify it.
            # https://forums.docker.com/t/docker-compose-set-container-name-and-hostname-dynamicaly/138259/2
            # "hostname": host_name,
            "domainname": env["OPENSTUDIOLANDSCAPES__DOMAIN_LAN"],
            # https://docs.docker.com/reference/compose-file/services/#restart
            "restart": "on-failure:3",
            "image": "${DOT_OVERRIDES_REGISTRY_NAMESPACE:-docker.io/openstudiolandscapes}/%s:%s"
            % (build["image_name"], build["image_tags"][0]),
            **copy.deepcopy(network_dict),
            **copy.deepcopy(volumes_dict),
            **copy.deepcopy(ports_dict),
            "command": deadline_command_compose_pulse_runner_10_2,
        }

        docker_dict["services"][service_name] = copy.deepcopy(service)

    docker_yaml = yaml.dump(docker_dict)

    yield Output(docker_dict)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(docker_dict),
            "docker_dict": MetadataValue.md(
                f"```json\n{json.dumps(docker_dict, indent=2)}\n```"
            ),
            "docker_yaml": MetadataValue.md(f"```yaml\n{docker_yaml}\n```"),
            "env": MetadataValue.json(env),
        },
    )


@asset(
    **ASSET_HEADER,
    ins={
        "env": AssetIn(
            AssetKey([*ASSET_HEADER["key_prefix"], "env"]),
        ),
        "build": AssetIn(
            AssetKey([*ASSET_HEADER["key_prefix"], "build_docker_image_client"]),
        ),
        "deadline_ini_10_2": AssetIn(
            AssetKey([*ASSET_HEADER["key_prefix"], "deadline_ini"]),
        ),
        "deadline_command_compose_worker_runner_10_2": AssetIn(
            AssetKey(
                [*ASSET_HEADER["key_prefix"], "deadline_command_compose_worker_runner"]
            ),
        ),
        "compose_networks_10_2": AssetIn(
            AssetKey([*ASSET_HEADER["key_prefix"], "compose_networks"]),
        ),
    },
)
def compose_worker_runner(
    context: AssetExecutionContext,
    env: dict,  # pylint: disable=redefined-outer-name
    build: dict,  # pylint: disable=redefined-outer-name
    deadline_ini_10_2: pathlib.Path,  # pylint: disable=redefined-outer-name
    deadline_command_compose_worker_runner_10_2: list,  # pylint: disable=redefined-outer-name
    compose_networks_10_2: dict,  # pylint: disable=redefined-outer-name
) -> Generator[Output[dict[str, dict[str, dict]]] | AssetMaterialization, None, None]:
    """ """

    network_dict = {}
    ports_dict = {}

    if "networks" in compose_networks_10_2:
        network_dict = {
            "networks": list(compose_networks_10_2.get("networks", {}).keys())
        }
        ports_dict = {
            "ports": [
                f"{env['DAGSTER_DEV_PORT_HOST']}:{env['DAGSTER_DEV_PORT_CONTAINER']}",
            ]
        }
    elif "network_mode" in compose_networks_10_2:
        network_dict = {"network_mode": compose_networks_10_2["network_mode"]}

    volumes_dict = {
        "volumes": [
            f"{deadline_ini_10_2.as_posix()}:/var/lib/Thinkbox/Deadline10/deadline.ini:ro",
            f"{env['REPOSITORY_INSTALL_DESTINATION_%s' % '__'.join(ASSET_HEADER_PARENT['key_prefix'])]}:/opt/Thinkbox/DeadlineRepository10",
        ]
    }

    # For portability, convert absolute volume paths to relative paths

    _volume_relative = []

    for v in volumes_dict["volumes"]:

        host, container = v.split(":", maxsplit=1)

        volume_dir_host_rel_path = get_relative_path_via_common_root(
            context=context,
            path_src=pathlib.Path(env["DOCKER_COMPOSE"]),
            path_dst=pathlib.Path(host),
            path_common_root=pathlib.Path(env["DOT_LANDSCAPES"]),
        )

        _volume_relative.append(
            f"{volume_dir_host_rel_path.as_posix()}:{container}",
        )

    volumes_dict = {
        "volumes": [
            *_volume_relative,
        ]
    }

    service_name_base = "deadline-10-2-worker"
    padding = 3

    docker_dict = {"services": {}}

    for i in range(NUM_SERVICES):
        service_name = f"{service_name_base}-{str(i+1).zfill(padding)}"
        container_name = "--".join([service_name, env.get("LANDSCAPE", "default")])
        # host_name = ".".join([env["HOSTNAME_WORKER_RUNNER"] or service_name, env["OPENSTUDIOLANDSCAPES__DOMAIN_LAN"]])

        deadline_command_compose_worker_runner_10_2.extend(["-name", str(service_name)])

        service = {
            "container_name": container_name,
            # To have a unique, dynamic hostname, we simply must not
            # specify it.
            # https://forums.docker.com/t/docker-compose-set-container-name-and-hostname-dynamicaly/138259/2
            # https://shantanoo-desai.github.io/posts/technology/hostname-docker-container/
            # "hostname": host_name,
            "domainname": env["OPENSTUDIOLANDSCAPES__DOMAIN_LAN"],
            "restart": "always",
            "image": "${DOT_OVERRIDES_REGISTRY_NAMESPACE:-docker.io/openstudiolandscapes}/%s:%s"
            % (build["image_name"], build["image_tags"][0]),
            **copy.deepcopy(network_dict),
            **copy.deepcopy(ports_dict),
            **copy.deepcopy(volumes_dict),
            "command": deadline_command_compose_worker_runner_10_2,
        }

        docker_dict["services"][service_name] = copy.deepcopy(service)

    docker_yaml = yaml.dump(docker_dict)

    yield Output(docker_dict)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(docker_dict),
            "docker_dict": MetadataValue.md(
                f"```json\n{json.dumps(docker_dict, indent=2)}\n```"
            ),
            "docker_yaml": MetadataValue.md(f"```yaml\n{docker_yaml}\n```"),
            "env": MetadataValue.json(env),
        },
    )


@asset(
    **ASSET_HEADER,
)
def compose_networks(
    context: AssetExecutionContext,
) -> Generator[
    Output[dict[str, dict[str, dict[str, str]]]] | AssetMaterialization, None, None
]:

    compose_network_mode = ComposeNetworkMode.HOST

    if compose_network_mode == ComposeNetworkMode.DEFAULT:
        docker_dict = {}

    else:
        docker_dict = {
            "network_mode": compose_network_mode.value,
        }

    docker_yaml = yaml.dump(docker_dict)

    yield Output(docker_dict)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(docker_dict),
            "docker_dict": MetadataValue.md(
                f"```json\n{json.dumps(docker_dict, indent=2)}\n```"
            ),
            "docker_yaml": MetadataValue.md(f"```shell\n{docker_yaml}\n```"),
        },
    )


@asset(
    **ASSET_HEADER,
    ins={
        "compose_worker_runner": AssetIn(
            AssetKey([*ASSET_HEADER["key_prefix"], "compose_worker_runner"]),
        ),
        "compose_pulse_runner": AssetIn(
            AssetKey([*ASSET_HEADER["key_prefix"], "compose_pulse_runner"]),
        ),
    },
)
def compose_maps(
    context: AssetExecutionContext,
    **kwargs,  # pylint: disable=redefined-outer-name
) -> Generator[Output[list[dict]] | AssetMaterialization, None, None]:

    ret = list(kwargs.values())

    yield Output(ret)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(ret),
        },
    )


# @asset(
#     **ASSET_HEADER,
#     ins={
#         "env": AssetIn(
#             AssetKey([*ASSET_HEADER["key_prefix"], "env"]),
#         ),
#         "cmd_docker_compose_up_dict": AssetIn(
#             AssetKey([*ASSET_HEADER["key_prefix"], "cmd_docker_compose_up"]),
#         ),
#         "compose_pulse_runner": AssetIn(
#             AssetKey([*ASSET_HEADER["key_prefix"], "compose_pulse_runner"]),
#         ),
#         "compose_worker_runner": AssetIn(
#             AssetKey([*ASSET_HEADER["key_prefix"], "compose_worker_runner"]),
#         ),
#     },
# )
# def compose_up_and_set_hostname(
#         context: AssetExecutionContext,
#         env: dict,  # pylint: disable=redefined-outer-name
#         cmd_docker_compose_up_dict: dict[str, list],  # pylint: disable=redefined-outer-name,
#         compose_pulse_runner: dict,  # pylint: disable=redefined-outer-name,
#         compose_worker_runner: dict,  # pylint: disable=redefined-outer-name,
# ):
#
#     # Todo:
#     #  - [x] for i in range(NUM_SERVICES): [...]
#     #  - [ ] cmd_compose_up_and_hostname can become pretty lengthy in case NUM_SERVICES is high
#     #        maybe there is a better way to tell bash to rename all the container hostnames
#
#     compose_pulse_runner_services = list(compose_pulse_runner["services"].keys())
#     compose_worker_runner_services = list(compose_worker_runner["services"].keys())
#
#     # Example cmd:
#     # /usr/bin/docker compose --file /home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-04-08-10-45-09-df78673952cc4499a80407d91bd404f4/Deadline_10_2_Worker__Deadline_10_2_Worker/Deadline_10_2_Worker__group_out/docker_compose/docker-compose.yml --project-name 2025-04-08-10-45-09-df78673952cc4499a80407d91bd404f4-worker up --detach --remove-orphans && sudo nsenter --target $(docker inspect -f '{{ .State.Pid }}' deadline-10-2-worker-001) --uts hostname "$(hostname -f)-nice-hack"
#
#     cmd_docker_compose_up = cmd_docker_compose_up_dict["cmd_docker_compose_up"]
#     # cmd_docker_compose_pull_up = cmd_docker_compose_up_dict["cmd_docker_compose_pull_up"]
#     # cmd_docker_compose_down = cmd_docker_compose_up_dict["cmd_docker_compose_down"]
#     cmd_docker_compose_logs = cmd_docker_compose_up_dict["cmd_docker_compose_logs"]
#
#     context.log.info(cmd_docker_compose_up)
#
#     cmd_docker_compose_up.extend(
#         [
#             # needs to be detached in order to get to do sudo
#             "--detach",
#         ]
#     )
#
#     exclude_from_quote = []
#
#     cmd_docker_compose_set_dynamic_hostnames = []
#
#     # Transform container hostnames
#     # - deadline-10-2-worker-001...nnn
#     # - deadline-10-2-pulse-worker-001...nnn
#     # into
#     # - $(hostname)-deadline-10-2-worker-001...nnn
#     # - $(hostname)-deadline-10-2-pulse-worker-001...nnn
#     for service_name in zip(
#             compose_worker_runner_services,
#             compose_pulse_runner_services,
#     ):
#
#         target_worker = "$(docker inspect -f '{{ .State.Pid }}' %s)" % "--".join([service_name[0], env.get("LANDSCAPE", "default")])
#         target_pulse = "$(docker inspect -f '{{ .State.Pid }}' %s)" % "--".join([service_name[1], env.get("LANDSCAPE", "default")])
#         hostname_worker = f"$(hostname)-{service_name[0]}"
#         hostname_pulse = f"$(hostname)-{service_name[1]}"
#
#         exclude_from_quote.extend(
#             [
#                 target_worker,
#                 target_pulse,
#                 hostname_worker,
#                 hostname_pulse
#             ]
#         )
#
#         cmd_docker_compose_set_dynamic_hostname_worker = [
#             shutil.which("sudo"),
#             shutil.which("nsenter"),
#             "--target", target_worker,
#             "--uts",
#             "hostname",
#             hostname_worker,
#         ]
#
#         cmd_docker_compose_set_dynamic_hostname_pulse = [
#             shutil.which("sudo"),
#             shutil.which("nsenter"),
#             "--target", target_pulse,
#             "--uts",
#             "hostname",
#             hostname_pulse,
#         ]
#
#         cmd_docker_compose_set_dynamic_hostnames.extend(
#             [
#                 *cmd_docker_compose_set_dynamic_hostname_worker,
#                 "&&",
#                 *cmd_docker_compose_set_dynamic_hostname_pulse,
#                 "&&",
#             ]
#         )
#
#     cmd_compose_up_and_hostname = [
#         *cmd_docker_compose_up,
#         "&&",
#         *cmd_docker_compose_set_dynamic_hostnames,
#         # "&&",
#         *cmd_docker_compose_logs,
#     ]
#
#     # What we have atm:
#     # /usr/bin/docker compose --file /home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-04-08-10-45-09-df78673952cc4499a80407d91bd404f4/Deadline_10_2_Worker__Deadline_10_2_Worker/Deadline_10_2_Worker__group_out/docker_compose/docker-compose.yml --project-name 2025-04-08-10-45-09-df78673952cc4499a80407d91bd404f4-worker up --remove-orphans --detach && /usr/bin/sudo /usr/bin/nsenter --target '$(docker inspect -f '"'"'{{ .State.Pid }}'"'"' deadline-10-2-worker-001)' --uts hostname ''"'"'$(hostname)-my-new-hostname'"'"'' && /usr/bin/docker compose --file /home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-04-08-10-45-09-df78673952cc4499a80407d91bd404f4/Deadline_10_2_Worker__Deadline_10_2_Worker/Deadline_10_2_Worker__group_out/docker_compose/docker-compose.yml --project-name 2025-04-08-10-45-09-df78673952cc4499a80407d91bd404f4-worker logs --follow
#     # Should be like:
#     # /usr/bin/docker compose --file /home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-04-08-10-45-09-df78673952cc4499a80407d91bd404f4/Deadline_10_2_Worker__Deadline_10_2_Worker/Deadline_10_2_Worker__group_out/docker_compose/docker-compose.yml --project-name 2025-04-08-10-45-09-df78673952cc4499a80407d91bd404f4-worker up --remove-orphans --detach && /usr/bin/sudo /usr/bin/nsenter --target $(docker inspect -f '{{ .State.Pid }}' deadline-10-2-worker-001) --uts hostname "$(hostname)-my-new-hostname" && /usr/bin/docker compose --file /home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-04-08-10-45-09-df78673952cc4499a80407d91bd404f4/Deadline_10_2_Worker__Deadline_10_2_Worker/Deadline_10_2_Worker__group_out/docker_compose/docker-compose.yml --project-name 2025-04-08-10-45-09-df78673952cc4499a80407d91bd404f4-worker logs --follow
#     # /usr/bin/docker compose --file /home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-04-08-10-45-09-df78673952cc4499a80407d91bd404f4/Deadline_10_2_Worker__Deadline_10_2_Worker/Deadline_10_2_Worker__group_out/docker_compose/docker-compose.yml --project-name 2025-04-08-10-45-09-df78673952cc4499a80407d91bd404f4-worker up --remove-orphans --detach && /usr/bin/sudo /usr/bin/nsenter --target $(docker inspect -f '{{ .State.Pid }}' deadline-10-2-worker-001) --uts hostname $(hostname)-my-new-hostname-1234 && /usr/bin/docker compose --file /home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-04-08-10-45-09-df78673952cc4499a80407d91bd404f4/Deadline_10_2_Worker__Deadline_10_2_Worker/Deadline_10_2_Worker__group_out/docker_compose/docker-compose.yml --project-name 2025-04-08-10-45-09-df78673952cc4499a80407d91bd404f4-worker logs --follow
#
#     yield Output(cmd_compose_up_and_hostname)
#
#     yield AssetMaterialization(
#         asset_key=context.asset_key,
#         metadata={
#             "cmd_compose_up_and_hostname": MetadataValue.path(
#                 " ".join(
#                     shlex.quote(s) if not s in [
#                         "&&",
#                         ";",
#                         *exclude_from_quote,
#                     ] else s
#                     for s in cmd_compose_up_and_hostname
#                 )
#             ),
#             "compose_worker_runner_services": MetadataValue.json(compose_worker_runner_services),
#             "compose_pulse_runner_services": MetadataValue.json(compose_pulse_runner_services),
#         },
#     )


@asset(
    **ASSET_HEADER,
    ins={
        "features_in": AssetIn(AssetKey([*ASSET_HEADER["key_prefix"], "group_in"])),
    },
)
def deadline_command_compose_worker_runner(
    context: AssetExecutionContext,
    features_in: dict,
) -> Generator[Output[list[str]] | AssetMaterialization, None, None]:

    context.log.info(features_in)

    deadline_command = features_in.pop("deadline_command_compose_worker_runner")
    context.log.info(deadline_command)

    yield Output(deadline_command)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(deadline_command),
        },
    )


@asset(
    **ASSET_HEADER,
    ins={
        "features_in": AssetIn(AssetKey([*ASSET_HEADER["key_prefix"], "group_in"])),
    },
)
def deadline_command_compose_pulse_runner(
    context: AssetExecutionContext,
    features_in: dict,
) -> Generator[Output[list[str]] | AssetMaterialization, None, None]:

    context.log.info(features_in)

    deadline_command = features_in.pop("deadline_command_compose_pulse_runner")
    context.log.info(deadline_command)

    yield Output(deadline_command)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(deadline_command),
        },
    )


@asset(
    **ASSET_HEADER,
    ins={},
)
def cmd_extend(
    context: AssetExecutionContext,
) -> Generator[Output[list[Any]] | AssetMaterialization | Any, Any, None]:

    ret = ["--detach"]

    yield Output(ret)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(ret),
        },
    )


@asset(
    **ASSET_HEADER,
    ins={
        "env": AssetIn(
            AssetKey([*ASSET_HEADER["key_prefix"], "env"]),
        ),
        "compose": AssetIn(
            AssetKey([*ASSET_HEADER["key_prefix"], "compose"]),
        ),
    },
)
def cmd_append(
    context: AssetExecutionContext,
    env: dict,  # pylint: disable=redefined-outer-name
    compose: dict,  # pylint: disable=redefined-outer-name,
) -> Generator[Output[dict[str, list[Any]]] | AssetMaterialization | Any, Any, None]:

    ret = {"cmd": [], "exclude_from_quote": []}

    compose_services = list(compose["services"].keys())

    # Example cmd:
    # /usr/bin/docker compose --file /home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-04-08-10-45-09-df78673952cc4499a80407d91bd404f4/Deadline_10_2_Worker__Deadline_10_2_Worker/Deadline_10_2_Worker__group_out/docker_compose/docker-compose.yml --project-name 2025-04-08-10-45-09-df78673952cc4499a80407d91bd404f4-worker up --detach --remove-orphans && sudo nsenter --target $(docker inspect -f '{{ .State.Pid }}' deadline-10-2-worker-001) --uts hostname "$(hostname -f)-nice-hack"

    # cmd_docker_compose_up.extend(
    #     [
    #         # needs to be detached in order to get to do sudo
    #         "--detach",
    #     ]
    # )

    exclude_from_quote = []

    cmd_docker_compose_set_dynamic_hostnames = []

    # Transform container hostnames
    # - deadline-10-2-worker-001...nnn
    # - deadline-10-2-pulse-worker-001...nnn
    # into
    # - $(hostname)-deadline-10-2-worker-001...nnn
    # - $(hostname)-deadline-10-2-pulse-worker-001...nnn
    for service_name in compose_services:

        target_worker = "$(docker inspect -f '{{ .State.Pid }}' %s)" % "--".join(
            [service_name, env.get("LANDSCAPE", "default")]
        )
        hostname_worker = f"$(hostname)-{service_name}"

        exclude_from_quote.extend(
            [
                target_worker,
                hostname_worker,
            ]
        )

        cmd_docker_compose_set_dynamic_hostname_worker = [
            shutil.which("sudo"),
            shutil.which("nsenter"),
            "--target",
            target_worker,
            "--uts",
            "hostname",
            hostname_worker,
        ]

        # Reference:
        # /usr/bin/docker --config /home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-07-23-00-51-15-1afae50517c5453b95c518ee0cd8e0aa/OpenStudioLandscapes_Base__OpenStudioLandscapes_Base/OpenStudioLandscapes_Base__docker_config_json compose --progress plain --file /home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-07-23-00-51-15-1afae50517c5453b95c518ee0cd8e0aa/Deadline_10_2_Worker__Deadline_10_2_Worker/Deadline_10_2_Worker__DOCKER_COMPOSE/docker_compose/docker-compose.yml --project-name 2025-07-23-00-51-15-1afae50517c5453b95c518ee0cd8e0aa-worker up --remove-orphans --detach && /usr/bin/sudo /usr/bin/nsenter --target $(docker inspect -f '{{ .State.Pid }}' deadline-10-2-worker-001--2025-07-23-00-51-15-1afae50517c5453b95c518ee0cd8e0aa) --uts hostname $(hostname)-deadline-10-2-worker-001 && /usr/bin/sudo /usr/bin/nsenter --target $(docker inspect -f '{{ .State.Pid }}' deadline-10-2-pulse-worker-001--2025-07-23-00-51-15-1afae50517c5453b95c518ee0cd8e0aa) --uts hostname $(hostname)-deadline-10-2-pulse-worker-001 \
        #     && /usr/bin/docker --config /home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-07-23-00-51-15-1afae50517c5453b95c518ee0cd8e0aa/OpenStudioLandscapes_Base__OpenStudioLandscapes_Base/OpenStudioLandscapes_Base__docker_config_json compose --progress plain --file /home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-07-23-00-51-15-1afae50517c5453b95c518ee0cd8e0aa/Deadline_10_2_Worker__Deadline_10_2_Worker/Deadline_10_2_Worker__DOCKER_COMPOSE/docker_compose/docker-compose.yml --project-name 2025-07-23-00-51-15-1afae50517c5453b95c518ee0cd8e0aa-worker logs --follow
        # Current:
        # Pre
        # /usr/bin/docker --config /home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-07-23-00-51-15-1afae50517c5453b95c518ee0cd8e0aa/OpenStudioLandscapes_Base__OpenStudioLandscapes_Base/OpenStudioLandscapes_Base__docker_config_json compose --progress plain --file /home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-07-23-00-51-15-1afae50517c5453b95c518ee0cd8e0aa/Deadline_10_2_Worker__Deadline_10_2_Worker/Deadline_10_2_Worker__DOCKER_COMPOSE/docker_compose/docker-compose.yml --project-name 2025-07-23-00-51-15-1afae50517c5453b95c518ee0cd8e0aa-worker up --remove-orphans --detach && /usr/bin/sudo /usr/bin/nsenter --target '$(docker inspect -f '"'"'{{ .State.Pid }}'"'"' deadline-10-2-pulse-worker-001--2025-07-23-00-51-15-1afae50517c5453b95c518ee0cd8e0aa)' --uts hostname '$(hostname)-deadline-10-2-pulse-worker-001' && /usr/bin/sudo /usr/bin/nsenter --target '$(docker inspect -f '"'"'{{ .State.Pid }}'"'"' deadline-10-2-worker-001--2025-07-23-00-51-15-1afae50517c5453b95c518ee0cd8e0aa)' --uts hostname '$(hostname)-deadline-10-2-worker-001'
        # Post
        #                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   && /usr/bin/sudo /usr/bin/nsenter --target $(docker inspect -f '{{ .State.Pid }}' deadline-10-2-pulse-worker-001--2025-07-23-00-51-15-1afae50517c5453b95c518ee0cd8e0aa) --uts hostname $(hostname)-deadline-10-2-pulse-worker-001 && /usr/bin/sudo /usr/bin/nsenter --target $(docker inspect -f '{{ .State.Pid }}' deadline-10-2-worker-001--2025-07-23-00-51-15-1afae50517c5453b95c518ee0cd8e0aa) --uts hostname $(hostname)-deadline-10-2-worker-001

        cmd_docker_compose_set_dynamic_hostnames.extend(
            [
                "&&",
                *cmd_docker_compose_set_dynamic_hostname_worker,
            ]
        )

    ret["cmd"].extend(cmd_docker_compose_set_dynamic_hostnames)
    ret["exclude_from_quote"].extend(
        [
            "&&",
            ";",
            *exclude_from_quote,
        ]
    )

    yield Output(ret)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(ret),
        },
    )
