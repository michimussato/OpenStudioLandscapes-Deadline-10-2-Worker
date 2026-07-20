[![ Logo OpenStudioLandscapes ](https://github.com/michimussato/OpenStudioLandscapes/raw/main/media/images/logo128.png)](https://github.com/michimussato/OpenStudioLandscapes)

***

1. [Feature: OpenStudioLandscapes-Deadline-10-2-Worker](#feature-openstudiolandscapes-deadline-10-2-worker)
   1. [Brief](#brief)
   2. [Clone](#clone)
      1. [Clone and Install](#clone-and-install)
      2. [Uninstall](#uninstall)
   3. [Configure](#configure)
      1. [Default Configuration](#default-configuration)
   4. [Local Development/Unit Testing/Debugging](#local-developmentunit-testingdebugging)
2. [External Resources](#external-resources)
   1. [Known Issues](#known-issues)
      1. [Failed to establish connection to due to a communication error.](#failed-to-establish-connection-to-due-to-a-communication-error)
3. [Community](#community)

***

This `README.md` was dynamically created with [OpenStudioLandscapesUtil-ReadmeGenerator](https://github.com/michimussato/OpenStudioLandscapesUtil-ReadmeGenerator).

***

# Feature: OpenStudioLandscapes-Deadline-10-2-Worker

## Brief

This is an extension to the OpenStudioLandscapes ecosystem. The full documentation of OpenStudioLandscapes is available [here](https://github.com/michimussato/OpenStudioLandscapes).

> [!NOTE]
> 
> You feel like writing your own Feature? Go and check out the 
> [OpenStudioLandscapes-Template](https://github.com/michimussato/OpenStudioLandscapes-Template).

## Clone

Clone this repository into `OpenStudioLandscapes/.features` (assuming the current working directory to be the Git repository root `./OpenStudioLandscapes`):

```shell
# cd OpenStudioLandscapes
source .venv/bin/activate
openstudiolandscapes clone-feature --repo=https://github.com/michimussato/OpenStudioLandscapes-Deadline-10-2-Worker.git
deactivate
# Check the resulting console output for installation instructions
```

If Feature repository was cloned locally already:

```shell
# cd OpenStudioLandscapes
source .venv/bin/activate
pip install --editable ./.features/<Feature>
deactivate
# Check the resulting console output for installation instructions
```

### Clone and Install

```shell
# cd OpenStudioLandscapes
source .venv/bin/activate
openstudiolandscapes clone-feature --repo=https://github.com/michimussato/OpenStudioLandscapes-Deadline-10-2-Worker.git --install
deactivate
```

### Uninstall

```shell
# cd OpenStudioLandscapes
source .venv/bin/activate
pip uninstall OpenStudioLandscapes-Deadline-10-2-Worker
deactivate
```

For more info on `pip` see [VCS Support of `pip`](https://pip.pypa.io/en/stable/topics/vcs-support/).

## Configure

OpenStudioLandscapes will search for a local config store. The default location is `~/.config/OpenStudioLandscapes/config-store/` but you can specify a different location if you need to.

> [!TIP]
> 
> To specify a config store location different from
> the default location, check out the OpenStudioLandscapes 
> [CLI Section](https://github.com/michimussato/OpenStudioLandscapes#cli)
> to find out how to do that.

A local config store location will be created if it doesn't exist, together with the `config.yml` files for each individual Feature.

> [!TIP]
> 
> The config store root will be initialized as a local Git
> controlled repository. This makes it easy to track changes
> you made to the `config.yml`.

The following settings are available in `OpenStudioLandscapes-Deadline-10-2-Worker` and are based on [`OpenStudioLandscapes-Deadline-10-2-Worker/tree/main/src/OpenStudioLandscapes/Deadline_10_2_Worker/config/models.py`](https://github.com/michimussato/OpenStudioLandscapes-Deadline-10-2-Worker/tree/main/src/OpenStudioLandscapes/Deadline_10_2_Worker/config/models.py).

### Default Configuration

<details open>
<summary><code>config.yml</code></summary>


```yaml
compose_scope:
  default: worker
  title: Compose Scope
  type: string
deadline_10_2__worker_storage:
  default: '{DOT_LANDSCAPES}/{LANDSCAPE}/{FEATURE}/storage'
  format: path
  title: Deadline 10 2  Worker Storage
  type: string
deadline_10_2_worker_NUM_SERVICES:
  default: 1
  description: Number of workers to simulate in parallel.
  exclusiveMinimum: 0
  title: Deadline 10 2 Worker Num Services
  type: integer
deadline_10_2_worker_PADDING:
  default: 3
  exclusiveMinimum: 0
  title: Deadline 10 2 Worker Padding
  type: integer
docker_compose:
  default: '{DOT_LANDSCAPES}/{LANDSCAPE}/{FEATURE}/docker_compose/docker-compose.yml'
  description: The path to the `docker-compose.yml` file.
  format: path
  title: Docker Compose
  type: string
enabled:
  default: false
  description: '# Not enabled by default because this Feature has some basic requirements,
    such as the installers.'
  title: Enabled
  type: boolean
env:
  additionalProperties: true
  title: Env
  type: object
feature_name:
  default: OpenStudioLandscapes-Deadline-10-2-Worker
  title: Feature Name
  type: string
group_name:
  default: OpenStudioLandscapes_Deadline_10_2_Worker
  title: Group Name
  type: string
key_prefixes:
  default:
  - OpenStudioLandscapes_Deadline_10_2_Worker
  items:
    type: string
  title: Key Prefixes
  type: array
local_bind_volumes:
  description: Here you can define Feature specific, arbitrary, absolute bind volume
    mappings.
  items:
    type: string
  title: Local Bind Volumes
  type: array
local_environment_variables:
  additionalProperties:
    type: string
  description: Here you can define Feature specific, arbitrary environment variables.
  title: Local Environment Variables
  type: object

```

</details>


## Local Development/Unit Testing/Debugging

This is for isolated development, unit testing and debugging. Instead of the [`OpenStudioLandscapes-Deadline-10-2-Worker/tree/main/src/OpenStudioLandscapes/Deadline_10_2_Worker/definitions.py`](https://github.com/michimussato/OpenStudioLandscapes-Deadline-10-2-Worker/tree/main/src/OpenStudioLandscapes/Deadline_10_2_Worker/definitions.py), the accompanying [`OpenStudioLandscapes-Deadline-10-2-Worker/tree/main/workspace.yaml`](https://github.com/michimussato/OpenStudioLandscapes-Deadline-10-2-Worker/tree/main/workspace.yaml) loads the [`OpenStudioLandscapes-Deadline-10-2-Worker/tree/main/src/OpenStudioLandscapes/Deadline_10_2_Worker/_definitions_with_upstream_specs.py`](https://github.com/michimussato/OpenStudioLandscapes-Deadline-10-2-Worker/tree/main/src/OpenStudioLandscapes/Deadline_10_2_Worker/_definitions_with_upstream_specs.py) which also contains [`AssetSpec`](https://release-1-9-13.archive.dagster-docs.io/api/dagster/assets#dagster.AssetSpec) definitions for upstream dependencies as [external assets](https://release-1-9-13.archive.dagster-docs.io/guides/build/assets/external-assets).

```shell
# cd ./.features/OpenStudioLandscapes-Deadline-10-2-Worker
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip setuptools setuptools_scm wheel
pip install --editable .[dev]
dagster dev --workspace workspace.yaml
```

***

# External Resources

This is an extension Feature for `OpenStudioLandscapes-Deadline-10-2`. For more information see the `README.md` there:

- [OpenStudioLandscapes-Deadline-10-2](https://github.com/michimussato/OpenStudioLandscapes-Deadline-10-2)

## Known Issues

### Failed to establish connection to  due to a communication error.

```generic
deadline-10-2-pulse-worker-001--2025-07-24-13-27-17-332a6900a9cf452f9d58fa57d2b6195a: ERROR: UpdateClient.MaybeSendRequestNow caught an exception: POST http://deadline-rcs-runner-10-2.farm.evil:8888/rcs/v1/update returned "One or more errors occurred. (Name or service not known (deadline-rcs-runner-10-2.farm.evil:8888))" (Deadline.Net.Clients.Http.DeadlineHttpRequestException)
deadline-10-2-pulse-worker-001--2025-07-24-13-27-17-332a6900a9cf452f9d58fa57d2b6195a: ERROR: DataController threw a configuration exception during initialization: Failed to establish connection to deadline-rcs-runner-10-2.farm.evil:8888 due to a communication error. (Deadline.Configuration.DeadlineConfigException)
deadline-10-2-pulse-worker-001--2025-07-24-13-27-17-332a6900a9cf452f9d58fa57d2b6195a: Could not connect to Deadline Repository: Failed to establish connection to deadline-rcs-runner-10-2.farm.evil:8888 due to a communication error.
deadline-10-2-pulse-worker-001--2025-07-24-13-27-17-332a6900a9cf452f9d58fa57d2b6195a: Deadline Pulse will try to connect again in 10 seconds...
deadline-10-2-worker-001--2025-07-24-13-27-17-332a6900a9cf452f9d58fa57d2b6195a: ERROR: UpdateClient.MaybeSendRequestNow caught an exception: POST http://deadline-rcs-runner-10-2.farm.evil:8888/rcs/v1/update returned "One or more errors occurred. (Name or service not known (deadline-rcs-runner-10-2.farm.evil:8888))" (Deadline.Net.Clients.Http.DeadlineHttpRequestException)
deadline-10-2-worker-001--2025-07-24-13-27-17-332a6900a9cf452f9d58fa57d2b6195a: ERROR: DataController threw a configuration exception during initialization: Failed to establish connection to deadline-rcs-runner-10-2.farm.evil:8888 due to a communication error. (Deadline.Configuration.DeadlineConfigException)
deadline-10-2-worker-001--2025-07-24-13-27-17-332a6900a9cf452f9d58fa57d2b6195a: Could not connect to Deadline Repository: Failed to establish connection to deadline-rcs-runner-10-2.farm.evil:8888 due to a communication error.
deadline-10-2-worker-001--2025-07-24-13-27-17-332a6900a9cf452f9d58fa57d2b6195a: Deadline Worker will try to connect again in 10 seconds...                
```

Make sure that the name gets resolved correctly.

```generic
$ nslookup deadline-rcs-runner-10-2.openstudiolandscapes.lan
Server:         192.168.1.10
Address:        192.168.1.10#53

** server can't find deadline-rcs-runner-10-2.openstudiolandscapes.lan: NXDOMAIN                
```

And add a DNS record or edit your `hosts` file so that `deadline-rcs-runner-10-2.openstudiolandscapes.lan` gets resolved correctly, as in this example:

```generic
$ nslookup deadline-rcs-runner-10-2.openstudiolandscapes.lan
Server:         192.168.1.10
Address:        192.168.1.10#53

deadline-rcs-runner-10-2.openstudiolandscapes.lan      canonical name = lenovo.openstudiolandscapes.lan.
Name:   lenovo.openstudiolandscapes.lan
Address: 192.168.1.50                
```

***

# Community

| Feature                                   | GitHub                                                                                                                                                 | Discord                                                                      |
| ----------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------- |
| OpenStudioLandscapes                      | [https://github.com/michimussato/OpenStudioLandscapes](https://github.com/michimussato/OpenStudioLandscapes)                                           | [# openstudiolandscapes-general](https://discord.gg/F6bDRWsHac)              |
| OpenStudioLandscapes-Ayon                 | [https://github.com/michimussato/OpenStudioLandscapes-Ayon](https://github.com/michimussato/OpenStudioLandscapes-Ayon)                                 | [# openstudiolandscapes-ayon](https://discord.gg/gd6etWAF3v)                 |
| OpenStudioLandscapes-Dagster              | [https://github.com/michimussato/OpenStudioLandscapes-Dagster](https://github.com/michimussato/OpenStudioLandscapes-Dagster)                           | [# openstudiolandscapes-dagster](https://discord.gg/jwB3DwmKvs)              |
| OpenStudioLandscapes-Deadline-10-2        | [https://github.com/michimussato/OpenStudioLandscapes-Deadline-10-2](https://github.com/michimussato/OpenStudioLandscapes-Deadline-10-2)               | [# openstudiolandscapes-deadline-10-2](https://discord.gg/p2UjxHk4Y3)        |
| OpenStudioLandscapes-Deadline-10-2-Worker | [https://github.com/michimussato/OpenStudioLandscapes-Deadline-10-2-Worker](https://github.com/michimussato/OpenStudioLandscapes-Deadline-10-2-Worker) | [# openstudiolandscapes-deadline-10-2-worker](https://discord.gg/ttkbfkzUmf) |
| OpenStudioLandscapes-Flamenco             | [https://github.com/michimussato/OpenStudioLandscapes-Flamenco](https://github.com/michimussato/OpenStudioLandscapes-Flamenco)                         | [# openstudiolandscapes-flamenco](https://discord.gg/EPrX5fzBCf)             |
| OpenStudioLandscapes-Flamenco-Worker      | [https://github.com/michimussato/OpenStudioLandscapes-Flamenco-Worker](https://github.com/michimussato/OpenStudioLandscapes-Flamenco-Worker)           | [# openstudiolandscapes-flamenco-worker](https://discord.gg/Sa2zFqSc4p)      |
| OpenStudioLandscapes-Grafana              | [https://github.com/michimussato/OpenStudioLandscapes-Grafana](https://github.com/michimussato/OpenStudioLandscapes-Grafana)                           | [# openstudiolandscapes-grafana](https://discord.gg/gEDQ8vJWDb)              |
| OpenStudioLandscapes-Kitsu                | [https://github.com/michimussato/OpenStudioLandscapes-Kitsu](https://github.com/michimussato/OpenStudioLandscapes-Kitsu)                               | [# openstudiolandscapes-kitsu](https://discord.gg/6cc6mkReJ7)                |
| OpenStudioLandscapes-LikeC4               | [https://github.com/michimussato/OpenStudioLandscapes-LikeC4](https://github.com/michimussato/OpenStudioLandscapes-LikeC4)                             | [# openstudiolandscapes-likec4](https://discord.gg/qAYYsKYF6V)               |
| OpenStudioLandscapes-OpenCue              | [https://github.com/michimussato/OpenStudioLandscapes-OpenCue](https://github.com/michimussato/OpenStudioLandscapes-OpenCue)                           | [# openstudiolandscapes-opencue](https://discord.gg/3DdCZKkVyZ)              |
| OpenStudioLandscapes-OpenCue-Worker       | [https://github.com/michimussato/OpenStudioLandscapes-OpenCue-Worker](https://github.com/michimussato/OpenStudioLandscapes-OpenCue-Worker)             | [# openstudiolandscapes-opencue-worker](https://discord.gg/n9fxxhHa3V)       |
| OpenStudioLandscapes-RustDeskServer       | [https://github.com/michimussato/OpenStudioLandscapes-RustDeskServer](https://github.com/michimussato/OpenStudioLandscapes-RustDeskServer)             | [# openstudiolandscapes-rustdeskserver](https://discord.gg/nJ8Ffd2xY3)       |
| OpenStudioLandscapes-Syncthing            | [https://github.com/michimussato/OpenStudioLandscapes-Syncthing](https://github.com/michimussato/OpenStudioLandscapes-Syncthing)                       | [# openstudiolandscapes-syncthing](https://discord.gg/upb9MCqb3X)            |
| OpenStudioLandscapes-Template             | [https://github.com/michimussato/OpenStudioLandscapes-Template](https://github.com/michimussato/OpenStudioLandscapes-Template)                         | [# openstudiolandscapes-template](https://discord.gg/J59GYp3Wpy)             |
| OpenStudioLandscapes-VERT                 | [https://github.com/michimussato/OpenStudioLandscapes-VERT](https://github.com/michimussato/OpenStudioLandscapes-VERT)                                 | [# openstudiolandscapes-vert](https://discord.gg/EPrX5fzBCf)                 |
| OpenStudioLandscapes-filebrowser          | [https://github.com/michimussato/OpenStudioLandscapes-filebrowser](https://github.com/michimussato/OpenStudioLandscapes-filebrowser)                   | [# openstudiolandscapes-filebrowser](https://discord.gg/stzNsZBmwk)          |
| OpenStudioLandscapes-n8n                  | [https://github.com/michimussato/OpenStudioLandscapes-n8n](https://github.com/michimussato/OpenStudioLandscapes-n8n)                                   | [# openstudiolandscapes-n8n](https://discord.gg/yFYrG999wE)                  |

To follow up on the previous LinkedIn publications, visit:

- [OpenStudioLandscapes on LinkedIn](https://www.linkedin.com/company/106731439/).
- [Search for tag #OpenStudioLandscapes on LinkedIn](https://www.linkedin.com/search/results/all/?keywords=%23openstudiolandscapes).

***

Last changed: **2026-07-20 11:20:12 UTC**