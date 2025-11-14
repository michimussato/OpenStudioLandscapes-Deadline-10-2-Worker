[![ Logo OpenStudioLandscapes ](https://github.com/michimussato/OpenStudioLandscapes/raw/main/media/images/logo128.png)](https://github.com/michimussato/OpenStudioLandscapes)

***

1. [Feature: OpenStudioLandscapes-Deadline-10-2-Worker](#feature-openstudiolandscapes-deadline-10-2-worker)
   1. [Brief](#brief)
   2. [Requirements](#requirements)
   3. [Install](#install)
      1. [This Feature](#this-feature)
   4. [Add to OpenStudioLandscapes](#add-to-openstudiolandscapes)
   5. [Testing](#testing)
      1. [pre-commit](#pre-commit)
      2. [nox](#nox)
   6. [Variables](#variables)
      1. [Feature Configs](#feature-configs)
2. [Community](#community)
3. [Instructions](#instructions)
   1. [Known Issues](#known-issues)
      1. [Failed to establish connection to due to a communication error.](#failed-to-establish-connection-to-due-to-a-communication-error)

***

This `README.md` was dynamically created with [OpenStudioLandscapesUtil-ReadmeGenerator](https://github.com/michimussato/OpenStudioLandscapesUtil-ReadmeGenerator).

***

# Feature: OpenStudioLandscapes-Deadline-10-2-Worker

## Brief

This is an extension to the OpenStudioLandscapes ecosystem. The full documentation of OpenStudioLandscapes is available [here](https://github.com/michimussato/OpenStudioLandscapes).

You feel like writing your own Feature? Go and check out the [OpenStudioLandscapes-Template](https://github.com/michimussato/OpenStudioLandscapes-Template).

## Requirements

- `python-3.11`
- `OpenStudioLandscapes`

## Install

### This Feature

Clone this repository into `OpenStudioLandscapes/.features`:

```shell
# cd .features
git clone https://github.com/michimussato/OpenStudioLandscapes-Deadline-10-2-Worker.git
```

Create `venv`:

```shell
# cd .features/OpenStudioLandscapes-Deadline-10-2-Worker
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools
```

Configure `venv`:

```shell
# cd .features/OpenStudioLandscapes-Deadline-10-2-Worker
pip install -e "../../[dev]"
pip install -e ".[dev]"
```

For more info see [VCS Support of pip](https://pip.pypa.io/en/stable/topics/vcs-support/).

## Add to OpenStudioLandscapes

Add the following code to `OpenStudioLandscapes.engine.features.FEATURES`:

```python
FEATURES.update(
    "OpenStudioLandscapes-Deadline-10-2-Worker": {
        "enabled": True|False,
        # - from ENVIRONMENT VARIABLE (.env):
        #   "enabled": get_bool_env("ENV_VAR")
        # - combined:
        #   "enabled": True|False or get_bool_env(
        #       "OPENSTUDIOLANDSCAPES__ENABLE_FEATURE_OPENSTUDIOLANDSCAPES_DEADLINE_10_2_WORKER"
        #   )
        "module": "OpenStudioLandscapes.Deadline_10_2_Worker.definitions",
        "compose_scope": ComposeScope.DEFAULT,
        "feature_config": OpenStudioLandscapesConfig.DEFAULT,
    }
)
```

## Testing

### pre-commit

- https://pre-commit.com
- https://pre-commit.com/hooks.html

```shell
pre-commit install
```

### nox

#### Generate Report

```shell
nox --no-error-on-missing-interpreters --report .nox/nox-report.json
```

#### Re-Generate this README

```shell
nox -v --add-timestamp --session readme
```

#### Generate Sphinx Documentation

```shell
nox -v --add-timestamp --session docs
```

#### pylint

```shell
nox -v --add-timestamp --session lint
```

##### pylint: disable=redefined-outer-name

- [`W0621`](https://pylint.pycqa.org/en/latest/user_guide/messages/warning/redefined-outer-name.html): Due to Dagsters way of piping arguments into assets.

#### SBOM

Acronym for Software Bill of Materials

```shell
nox -v --add-timestamp --session sbom
```

We create the following SBOMs:

- [`cyclonedx-bom`](https://pypi.org/project/cyclonedx-bom/)
- [`pipdeptree`](https://pypi.org/project/pipdeptree/) (Dot)
- [`pipdeptree`](https://pypi.org/project/pipdeptree/) (Mermaid)

SBOMs for the different Python interpreters defined in [`.noxfile.VERSIONS`](https://github.com/michimussato/OpenStudioLandscapes-Deadline-10-2-Worker/tree/main/noxfile.py) will be created in the [`.sbom`](https://github.com/michimussato/OpenStudioLandscapes-Deadline-10-2-Worker/tree/main/.sbom) directory of this repository.

- `cyclone-dx`
- `pipdeptree` (Dot)
- `pipdeptree` (Mermaid)

Currently, the following Python interpreters are enabled for testing:

- `python3.11`

## Variables

The following variables are being declared in `OpenStudioLandscapes.Deadline_10_2_Worker.constants` and are accessible throughout the [`OpenStudioLandscapes-Deadline-10-2-Worker`](https://github.com/michimussato/OpenStudioLandscapes-Deadline-10-2-Worker/tree/main/src/OpenStudioLandscapes/Deadline_10_2_Worker/constants.py) package.

| Variable              | Type   |
| :-------------------- | :----- |
| `DOCKER_USE_CACHE`    | `bool` |
| `ASSET_HEADER_PARENT` | `dict` |
| `NUM_SERVICES`        | `int`  |
| `ASSET_HEADER`        | `dict` |
| `FEATURE_CONFIGS`     | `dict` |

### Feature Configs

#### Feature Config: default

| Variable                    | Type   | Value   |
| :-------------------------- | :----- | :------ |
| `DOCKER_USE_CACHE`          | `bool` | `False` |
| `HOSTNAME_PULSE_RUNNER`     | `str`  | ``      |
| `HOSTNAME_WORKER_RUNNER`    | `str`  | ``      |
| `TELEPORT_ENTRY_POINT_HOST` | `str`  | ``      |
| `TELEPORT_ENTRY_POINT_PORT` | `str`  | ``      |

# Community

| Feature                              | GitHub                                                                                                                                       | Discord                                                                 |
| ------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| OpenStudioLandscapes                 | [https://github.com/michimussato/OpenStudioLandscapes](https://github.com/michimussato/OpenStudioLandscapes)                                 | [# openstudiolandscapes-general](https://discord.gg/F6bDRWsHac)         |
| OpenStudioLandscapes-Ayon            | [https://github.com/michimussato/OpenStudioLandscapes-Ayon](https://github.com/michimussato/OpenStudioLandscapes-Ayon)                       | [# openstudiolandscapes-ayon](https://discord.gg/gd6etWAF3v)            |
| OpenStudioLandscapes-Dagster         | [https://github.com/michimussato/OpenStudioLandscapes-Dagster](https://github.com/michimussato/OpenStudioLandscapes-Dagster)                 | [# openstudiolandscapes-dagster](https://discord.gg/jwB3DwmKvs)         |
| OpenStudioLandscapes-Flamenco        | [https://github.com/michimussato/OpenStudioLandscapes-Flamenco](https://github.com/michimussato/OpenStudioLandscapes-Flamenco)               | [# openstudiolandscapes-flamenco](https://discord.gg/EPrX5fzBCf)        |
| OpenStudioLandscapes-Flamenco-Worker | [https://github.com/michimussato/OpenStudioLandscapes-Flamenco-Worker](https://github.com/michimussato/OpenStudioLandscapes-Flamenco-Worker) | [# openstudiolandscapes-flamenco-worker](https://discord.gg/Sa2zFqSc4p) |
| OpenStudioLandscapes-Kitsu           | [https://github.com/michimussato/OpenStudioLandscapes-Kitsu](https://github.com/michimussato/OpenStudioLandscapes-Kitsu)                     | [# openstudiolandscapes-kitsu](https://discord.gg/6cc6mkReJ7)           |
| OpenStudioLandscapes-RustDeskServer  | [https://github.com/michimussato/OpenStudioLandscapes-RustDeskServer](https://github.com/michimussato/OpenStudioLandscapes-RustDeskServer)   | [# openstudiolandscapes-rustdeskserver](https://discord.gg/nJ8Ffd2xY3)  |
| OpenStudioLandscapes-Template        | [https://github.com/michimussato/OpenStudioLandscapes-Template](https://github.com/michimussato/OpenStudioLandscapes-Template)               | [# openstudiolandscapes-template](https://discord.gg/J59GYp3Wpy)        |
| OpenStudioLandscapes-VERT            | [https://github.com/michimussato/OpenStudioLandscapes-VERT](https://github.com/michimussato/OpenStudioLandscapes-VERT)                       | [# openstudiolandscapes-twingate](https://discord.gg/FYaFRUwbYr)        |

To follow up on the previous LinkedIn publications, visit:

- [OpenStudioLandscapes on LinkedIn](https://www.linkedin.com/company/106731439/).
- [Search for tag #OpenStudioLandscapes on LinkedIn](https://www.linkedin.com/search/results/all/?keywords=%23openstudiolandscapes).

***

# Instructions

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