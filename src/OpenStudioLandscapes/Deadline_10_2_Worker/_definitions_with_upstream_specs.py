from dagster import Definitions
from OpenStudioLandscapes.Deadline_10_2.assets import (
    build_docker_image_client_spec,
    # compose_pulse_runner_spec,
    # compose_pulse_runner,
    deadline_command_compose_pulse_runner_spec,
    deadline_command_compose_worker_runner_spec,
    feature_out_v2,
)
from OpenStudioLandscapes.engine.base.assets import group_out_base_spec

from OpenStudioLandscapes.Deadline_10_2_Worker.definitions import assets_base


# from OpenStudioLandscapes.Deadline_10_2.assets import feature_out_v2

assets_external = []
assets_external.append(group_out_base_spec)
# assets_external.append(compose_pulse_runner_spec)
# assets_external.extend(compose_pulse_runner.specs)
assets_external.append(deadline_command_compose_worker_runner_spec)
assets_external.append(deadline_command_compose_pulse_runner_spec)
assets_external.append(build_docker_image_client_spec)
assets_external.extend(feature_out_v2.specs)


defs = Definitions(
    assets=[
        *assets_base,
        *assets_external,
    ],
)
