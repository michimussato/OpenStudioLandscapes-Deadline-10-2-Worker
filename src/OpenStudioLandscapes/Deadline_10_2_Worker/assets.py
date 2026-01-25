import copy
import enum
import pathlib
import shutil
import textwrap
import urllib.parse
from typing import Any, Dict, Generator, List, Union

import yaml
from dagster import (
    AssetExecutionContext,
    AssetIn,
    AssetKey,
    AssetMaterialization,
    AssetsDefinition,
    MetadataValue,
    Output,
    asset,
)

# Override default ConfigParent
from OpenStudioLandscapes.Deadline_10_2.config.models import Config as ConfigParent
from OpenStudioLandscapes.Deadline_10_2.constants import (
    ASSET_HEADER as ASSET_HEADER_FEATURE_IN,
)
from OpenStudioLandscapes.engine.common_assets.compose import get_compose
from OpenStudioLandscapes.engine.common_assets.docker_compose_graph import (
    get_docker_compose_graph,
)
from OpenStudioLandscapes.engine.common_assets.feature import get_feature__CONFIG
from OpenStudioLandscapes.engine.common_assets.feature_out import get_feature_out_v2
from OpenStudioLandscapes.engine.common_assets.group_in import (
    get_feature_in,
    get_feature_in_parent,
)
from OpenStudioLandscapes.engine.common_assets.group_out import get_group_out
from OpenStudioLandscapes.engine.config.models import ConfigEngine
from OpenStudioLandscapes.engine.constants import ASSET_HEADER_BASE
from OpenStudioLandscapes.engine.enums import *
from OpenStudioLandscapes.engine.utils import *
from OpenStudioLandscapes.engine.utils.docker.compose_dicts import *

from OpenStudioLandscapes.Deadline_10_2_Worker import dist
from OpenStudioLandscapes.Deadline_10_2_Worker.config.models import CONFIG_STR, Config
from OpenStudioLandscapes.Deadline_10_2_Worker.constants import *

# https://github.com/yaml/pyyaml/issues/722#issuecomment-1969292770
yaml.SafeDumper.add_multi_representer(
    data_type=enum.Enum,
    representer=yaml.representer.SafeRepresenter.represent_str,
)


# Overridden locally
# cmd: AssetsDefinition = get_feature__cmd(
#     ASSET_HEADER=ASSET_HEADER,
# )


CONFIG: AssetsDefinition = get_feature__CONFIG(
    ASSET_HEADER=ASSET_HEADER,
    CONFIG_STR=CONFIG_STR,
    search_model_of_type=Config,
)

feature_in: AssetsDefinition = get_feature_in(
    ASSET_HEADER=ASSET_HEADER,
    ASSET_HEADER_BASE=ASSET_HEADER_BASE,
    ASSET_HEADER_FEATURE_IN=ASSET_HEADER_FEATURE_IN,
)

group_out: AssetsDefinition = get_group_out(
    ASSET_HEADER=ASSET_HEADER,
)


docker_compose_graph: AssetsDefinition = get_docker_compose_graph(
    ASSET_HEADER=ASSET_HEADER,
)


compose: AssetsDefinition = get_compose(
    ASSET_HEADER=ASSET_HEADER,
)

feature_out_v2: AssetsDefinition = get_feature_out_v2(
    ASSET_HEADER=ASSET_HEADER,
)


# Produces
# - feature_in_parent
# - CONFIG_PARENT
# if ConfigParent is or type FeatureBaseModel
feature_in_parent: Union[AssetsDefinition, None] = get_feature_in_parent(
    ASSET_HEADER=ASSET_HEADER,
    config_parent=ConfigParent,
)


# Todo:
#  - [ ] Create dynamic yet persistent hostname so that we can use THE SAME
#        docker-compose file on an arbitrary number of hosts without conflicts
#        - https://forums.docker.com/t/change-hostname-of-an-existing-container/361/16
#          `docker inspect -f '{{ .State.Pid }}' deadline-10-2-worker-001`
#          `sudo nsenter --target 400453 --uts`
#          One line (enter ns): `sudo nsenter --target $(docker inspect -f '{{ .State.Pid }}' deadline-10-2-worker-001) --uts`
#          One line (run command): `sudo nsenter --target $(docker inspect -f '{{ .State.Pid }}' deadline-10-2-worker-001) --uts hostname "new-hostname"`
#          One line (run command): `sudo nsenter --target $(docker inspect -f '{{ .State.Pid }}' deadline-10-2-worker-001) --uts hostname "$(hostname)-new-hostname"`


@asset(
    **ASSET_HEADER,
    ins={
        "CONFIG": AssetIn(
            AssetKey([*ASSET_HEADER["key_prefix"], "CONFIG"]),
        ),
        "CONFIG_PARENT": AssetIn(
            AssetKey([*ASSET_HEADER["key_prefix"], "CONFIG_PARENT"]),
        ),
    },
)
def deadline_ini(
    context: AssetExecutionContext,
    CONFIG: Config,
    CONFIG_PARENT: ConfigParent,
    # Todo:
) -> Generator[Output[pathlib.Path] | AssetMaterialization, None, None]:

    env: Dict = CONFIG.env

    config_engine: ConfigEngine = CONFIG.config_engine

    # @formatter:off
    deadline_ini = textwrap.dedent("""\
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
        """).format(
        auto_generated=f"AUTO-GENERATED by Dagster Asset {'__'.join(context.asset_key.path)}",
        dagster_url=urllib.parse.quote(
            f"http://localhost:3000/asset-groups/{'%2F'.join(context.asset_key.path)}",
            safe=":/%",
        ),
        rcs_runner_hostname=".".join(
            ["deadline-rcs-runner-10-2", config_engine.openstudiolandscapes__domain_lan]
        ),
        RCS_HTTP_PORT_HOST=CONFIG_PARENT.deadline_10_2_RCS_HTTP_PORT_HOST,
        WEBSERVICE_HTTP_PORT_HOST=CONFIG_PARENT.deadline_10_2_WEBSERVICE_HTTP_PORT_HOST,
        # **env,
    )
    # @formatter:on

    deadline_client_ini = pathlib.Path(
        env["DOT_LANDSCAPES"],
        env.get("LANDSCAPE", "default"),
        f"{dist.name}",
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
        },
    )


@asset(
    **ASSET_HEADER,
    ins={
        "CONFIG": AssetIn(
            AssetKey([*ASSET_HEADER["key_prefix"], "CONFIG"]),
        ),
        "CONFIG_PARENT": AssetIn(
            AssetKey([*ASSET_HEADER["key_prefix"], "CONFIG_PARENT"]),
        ),
        "build_docker_image_client": AssetIn(
            AssetKey(
                [*ASSET_HEADER_FEATURE_IN["key_prefix"], "build_docker_image_client"]
            ),
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
    CONFIG: Config,
    CONFIG_PARENT: ConfigParent,
    build_docker_image_client: Dict,  # pylint: disable=redefined-outer-name
    deadline_ini_10_2: pathlib.Path,  # pylint: disable=redefined-outer-name
    deadline_command_compose_pulse_runner_10_2: List,  # pylint: disable=redefined-outer-name
    compose_networks_10_2: Dict,  # pylint: disable=redefined-outer-name
) -> Generator[Output[Dict[str, Dict[str, Dict]]] | AssetMaterialization, None, None]:
    """ """

    env: Dict = CONFIG.env

    config_engine: ConfigEngine = CONFIG.config_engine

    service_name_base = "deadline-10-2-pulse-worker"

    docker_dict = {"services": {}}

    for i in range(CONFIG.deadline_10_2_worker_NUM_SERVICES):

        if CONFIG.validate_deadline_10_2_worker_NUM_SERVICES == 1:
            # Ignore incrementation
            service_name = f"{service_name_base}"

        else:
            service_name = f"{service_name_base}-{str(i+1).zfill(CONFIG.deadline_10_2_worker_PADDING)}"

        container_name, _ = get_docker_compose_names(
            context=context,
            service_name=service_name,
            landscape_id=env.get("LANDSCAPE", "default"),
            domain_lan=config_engine.openstudiolandscapes__domain_lan,
        )
        # container_name = "--".join([service_name, env.get("LANDSCAPE", "default")])
        # host_name = ".".join([env["HOSTNAME_PULSE_RUNNER"] or service_name, env["OPENSTUDIOLANDSCAPES__DOMAIN_LAN"]])

        network_dict = {}
        ports_dict = {}

        if "networks" in compose_networks_10_2:
            network_dict = {
                "networks": list(compose_networks_10_2.get("networks", {}).keys())
            }
            ports_dict = {"ports": []}
        elif "network_mode" in compose_networks_10_2:
            network_dict = {"network_mode": compose_networks_10_2["network_mode"]}

        volumes_dict = {
            "volumes": [
                f"{deadline_ini_10_2.as_posix()}:/var/lib/Thinkbox/Deadline10/deadline.ini:ro",
                f"{CONFIG_PARENT.deadline_10_2_repository_install_destination_expanded.as_posix()}:/opt/Thinkbox/DeadlineRepository10",
            ]
        }

        # For portability, convert absolute volume paths to relative paths

        _volume_relative = []

        for v in volumes_dict["volumes"]:

            host, container = v.split(":", maxsplit=1)

            volume_dir_host_rel_path = get_relative_path_via_common_root(
                context=context,
                path_src=CONFIG.docker_compose_expanded,
                path_dst=pathlib.Path(host),
                path_common_root=pathlib.Path(env["DOT_LANDSCAPES"]),
            )

            _volume_relative.append(
                f"{volume_dir_host_rel_path.as_posix()}:{container}",
            )

        volumes_dict = {
            "volumes": list(
                {
                    *_volume_relative,
                    *config_engine.global_bind_volumes,
                    *CONFIG.local_bind_volumes,
                }
            )
        }

        service = {
            "container_name": container_name,
            # To have a unique, dynamic hostname, we simply must not
            # specify it.
            # https://forums.docker.com/t/docker-compose-set-container-name-and-hostname-dynamicaly/138259/2
            # "hostname": host_name,
            "domainname": config_engine.openstudiolandscapes__domain_lan,
            # https://docs.docker.com/reference/compose-file/services/#restart
            "restart": f"{DockerComposePolicies.RESTART_POLICY.ON_FAILURE.value}:3",
            # "image": "${DOT_OVERRIDES_REGISTRY_NAMESPACE:-docker.io/openstudiolandscapes}/%s:%s"
            # % (build["image_name"], build["image_tags"][0]),
            "image": "%s%s:%s"
            % (
                build_docker_image_client["image_prefixes"],
                build_docker_image_client["image_name"],
                build_docker_image_client["image_tags"][0],
            ),
            "environment": {
                **config_engine.global_environment_variables,
                **CONFIG.local_environment_variables,
            },
            **copy.deepcopy(network_dict),
            **copy.deepcopy(volumes_dict),
            **copy.deepcopy(ports_dict),
            # # deadlinepulse does not have a -name flag
            # deadline_command_compose_pulse_runner_10_2.extend(
            #     [
            #         "-name",
            #         str(service_name)
            #     ]
            # )
            "command": deadline_command_compose_pulse_runner_10_2,
        }

        docker_dict["services"][service_name] = copy.deepcopy(service)

    docker_yaml = yaml.dump(docker_dict)

    yield Output(docker_dict)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(docker_dict),
            "docker_yaml": MetadataValue.md(f"```yaml\n{docker_yaml}\n```"),
        },
    )


@asset(
    **ASSET_HEADER,
    ins={
        "CONFIG": AssetIn(
            AssetKey([*ASSET_HEADER["key_prefix"], "CONFIG"]),
        ),
        "CONFIG_PARENT": AssetIn(
            AssetKey([*ASSET_HEADER["key_prefix"], "CONFIG_PARENT"]),
        ),
        "build_docker_image_client": AssetIn(
            AssetKey(
                [*ASSET_HEADER_FEATURE_IN["key_prefix"], "build_docker_image_client"]
            ),
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
    CONFIG: Config,  # pylint: disable=redefined-outer-name
    CONFIG_PARENT: ConfigParent,  # pylint: disable=redefined-outer-name
    build_docker_image_client: Dict,  # pylint: disable=redefined-outer-name
    deadline_ini_10_2: pathlib.Path,  # pylint: disable=redefined-outer-name
    deadline_command_compose_worker_runner_10_2: List,  # pylint: disable=redefined-outer-name
    compose_networks_10_2: Dict,  # pylint: disable=redefined-outer-name
) -> Generator[Output[Dict[str, Dict[str, Dict]]] | AssetMaterialization, None, None]:
    """ """

    env: Dict = CONFIG.env

    config_engine: ConfigEngine = CONFIG.config_engine

    service_name_base = "deadline-10-2-worker"

    docker_dict = {"services": {}}

    for i in range(CONFIG.deadline_10_2_worker_NUM_SERVICES):

        if CONFIG.deadline_10_2_worker_NUM_SERVICES == 1:
            # Ignore incrementation
            service_name = f"{service_name_base}"

        else:
            service_name = f"{service_name_base}-{str(i+1).zfill(CONFIG.deadline_10_2_worker_PADDING)}"

        container_name, _ = get_docker_compose_names(
            context=context,
            service_name=service_name,
            landscape_id=env.get("LANDSCAPE", "default"),
            domain_lan=config_engine.openstudiolandscapes__domain_lan,
        )

        network_dict = {}
        ports_dict = {}

        if "networks" in compose_networks_10_2:
            network_dict = {
                "networks": list(compose_networks_10_2.get("networks", {}).keys())
            }
            ports_dict = {"ports": []}
        elif "network_mode" in compose_networks_10_2:
            network_dict = {"network_mode": compose_networks_10_2["network_mode"]}

        volumes_dict = {
            "volumes": [
                f"{deadline_ini_10_2.as_posix()}:/var/lib/Thinkbox/Deadline10/deadline.ini:ro",
                f"{CONFIG_PARENT.deadline_10_2_repository_install_destination_expanded.as_posix()}:/opt/Thinkbox/DeadlineRepository10",
            ]
        }

        # For portability, convert absolute volume paths to relative paths

        _volume_relative = []

        for v in volumes_dict["volumes"]:

            host, container = v.split(":", maxsplit=1)

            volume_dir_host_rel_path = get_relative_path_via_common_root(
                context=context,
                path_src=CONFIG.docker_compose_expanded,
                path_dst=pathlib.Path(host),
                path_common_root=pathlib.Path(env["DOT_LANDSCAPES"]),
            )

            _volume_relative.append(
                f"{volume_dir_host_rel_path.as_posix()}:{container}",
            )

        volumes_dict = {
            "volumes": list(
                {
                    *_volume_relative,
                    *config_engine.global_bind_volumes,
                    *CONFIG.local_bind_volumes,
                }
            )
        }

        deadline_command_compose_worker_runner_10_2.extend(["-name", str(service_name)])

        service = {
            "container_name": container_name,
            # To have a unique, dynamic hostname, we simply must not
            # specify it.
            # https://forums.docker.com/t/docker-compose-set-container-name-and-hostname-dynamicaly/138259/2
            # https://shantanoo-desai.github.io/posts/technology/hostname-docker-container/
            # "hostname": host_name,
            "domainname": config_engine.openstudiolandscapes__domain_lan,
            "restart": DockerComposePolicies.RESTART_POLICY.ALWAYS.value,
            # "image": "${DOT_OVERRIDES_REGISTRY_NAMESPACE:-docker.io/openstudiolandscapes}/%s:%s"
            # % (build["image_name"], build["image_tags"][0]),
            "image": "%s%s:%s"
            % (
                build_docker_image_client["image_prefixes"],
                build_docker_image_client["image_name"],
                build_docker_image_client["image_tags"][0],
            ),
            "environment": {
                **config_engine.global_environment_variables,
                **CONFIG.local_environment_variables,
            },
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
            "docker_yaml": MetadataValue.md(f"```yaml\n{docker_yaml}\n```"),
        },
    )


@asset(
    **ASSET_HEADER,
    ins={
        "CONFIG": AssetIn(
            AssetKey([*ASSET_HEADER["key_prefix"], "CONFIG"]),
        ),
    },
)
def compose_networks(
    context: AssetExecutionContext,
    CONFIG: Config,  # pylint: disable=redefined-outer-name
) -> Generator[
    Output[Dict[str, Dict[str, Dict[str, str]]]] | AssetMaterialization, None, None
]:

    env: Dict = CONFIG.env

    compose_network_mode = DockerComposePolicies.NETWORK_MODE.HOST

    docker_dict = get_network_dicts(
        context=context,
        compose_network_mode=compose_network_mode,
        env=env,
    )

    docker_yaml = yaml.dump(docker_dict)

    yield Output(docker_dict)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(docker_dict),
            "docker_yaml": MetadataValue.md(f"```yaml\n{docker_yaml}\n```"),
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
) -> Generator[Output[List[Dict]] | AssetMaterialization, None, None]:

    ret = list(kwargs.values())

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
        "deadline_command_compose_worker_runner": AssetIn(
            AssetKey(
                [
                    *ASSET_HEADER_FEATURE_IN["key_prefix"],
                    "deadline_command_compose_worker_runner",
                ]
            ),
        ),
    },
)
def deadline_command_compose_worker_runner(
    context: AssetExecutionContext,
    deadline_command_compose_worker_runner: List,
) -> Generator[Output[List[str]] | AssetMaterialization, None, None]:

    yield Output(deadline_command_compose_worker_runner)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(
                deadline_command_compose_worker_runner
            ),
        },
    )


@asset(
    **ASSET_HEADER,
    ins={
        "deadline_command_compose_pulse_runner": AssetIn(
            AssetKey(
                [
                    *ASSET_HEADER_FEATURE_IN["key_prefix"],
                    "deadline_command_compose_pulse_runner",
                ]
            ),
        ),
    },
)
def deadline_command_compose_pulse_runner(
    context: AssetExecutionContext,
    deadline_command_compose_pulse_runner: List,  # pylint: disable=redefined-outer-name
) -> Generator[Output[List[str]] | AssetMaterialization, None, None]:

    yield Output(deadline_command_compose_pulse_runner)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(
                deadline_command_compose_pulse_runner
            ),
        },
    )


@asset(
    **ASSET_HEADER,
    ins={},
)
def cmd_extend(
    context: AssetExecutionContext,
) -> Generator[Output[List[Any]] | AssetMaterialization | Any, Any, None]:

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
        "CONFIG": AssetIn(
            AssetKey([*ASSET_HEADER["key_prefix"], "CONFIG"]),
        ),
        "compose": AssetIn(
            AssetKey([*ASSET_HEADER["key_prefix"], "compose"]),
        ),
    },
)
def cmd_append(
    context: AssetExecutionContext,
    CONFIG: Config,  # pylint: disable=redefined-outer-name
    compose: Dict,  # pylint: disable=redefined-outer-name,
) -> Generator[Output[Dict[str, List[Any]]] | AssetMaterialization | Any, Any, None]:

    env: Dict = CONFIG.env

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
    # - ${HOSTNAME}-deadline-10-2-worker-001...nnn
    # - ${HOSTNAME}-deadline-10-2-pulse-worker-001...nnn
    #
    # We do this because this worker might be running on
    # a machine which hostname we don't know at build time
    # so the machine name needs to be extracted and forwarded
    # to the Docker container.
    # Note: $HOSTNAME is not defined (at least on some OSs)
    # so we have to set it in the "up"-scripts
    for service_name in compose_services:

        target_worker = (
            "\"$($(which docker) inspect -f '{{ .State.Pid }}' %s)\""
            % ".".join([service_name, env.get("LANDSCAPE", "default")])
        )
        hostname_worker = f"${{HOSTNAME}}-{service_name}"

        exclude_from_quote.extend(
            [
                target_worker,
                hostname_worker,
            ]
        )

        cmd_docker_compose_set_dynamic_hostname_worker = [
            shutil.which("sudo"),
            "--stdin",
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
            "$(which docker)",
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
