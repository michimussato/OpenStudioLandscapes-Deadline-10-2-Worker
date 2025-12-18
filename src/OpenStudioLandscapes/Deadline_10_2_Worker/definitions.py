from dagster import (
    Definitions,
    load_assets_from_modules,
)

import OpenStudioLandscapes.Deadline_10_2_Worker.assets

assets = load_assets_from_modules(
    modules=[OpenStudioLandscapes.Deadline_10_2_Worker.assets],
)


defs = Definitions(
    assets=[
        *assets,
    ],
)
