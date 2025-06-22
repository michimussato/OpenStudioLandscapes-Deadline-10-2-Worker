from dagster import (
    Definitions,
    load_assets_from_modules,
)

import OpenStudioLandscapes.Deadline_10_2_Worker.assets
import OpenStudioLandscapes.Deadline_10_2_Worker.constants

assets = load_assets_from_modules(
    modules=[OpenStudioLandscapes.Deadline_10_2_Worker.assets],
)

constants = load_assets_from_modules(
    modules=[OpenStudioLandscapes.Deadline_10_2_Worker.constants],
)


defs = Definitions(
    assets=[
        *assets,
        *constants,
    ],
)
