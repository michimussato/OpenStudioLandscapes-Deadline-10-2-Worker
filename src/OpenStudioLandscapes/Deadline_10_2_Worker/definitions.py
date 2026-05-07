from dagster import (
    Definitions,
    load_assets_from_modules,
)

import OpenStudioLandscapes.Deadline_10_2_Worker.assets
from OpenStudioLandscapes.Deadline_10_2_Worker import *

LOGGER.info(f"Loading {dist.name} assets...")

assets_base = load_assets_from_modules(
    modules=[OpenStudioLandscapes.Deadline_10_2_Worker.assets],
)


defs = Definitions(
    assets=[
        *assets_base,
    ],
)
