from dagster import Definitions
from OpenStudioLandscapes.Deadline_10_2.assets import (
    build_docker_image_client,
    deadline_command_compose_pulse_runner,
    deadline_command_compose_worker_runner,
    feature_out_v2,
)
from OpenStudioLandscapes.engine.base.assets import group_out_base

from OpenStudioLandscapes.Deadline_10_2_Worker.definitions import assets_base

assets_external = []
assets_external.extend(group_out_base.specs)
assets_external.extend(deadline_command_compose_worker_runner.specs)
assets_external.extend(deadline_command_compose_pulse_runner.specs)
assets_external.extend(build_docker_image_client.specs)
assets_external.extend(feature_out_v2.specs)


defs = Definitions(
    assets=[
        *assets_base,
        *assets_external,
    ],
)
