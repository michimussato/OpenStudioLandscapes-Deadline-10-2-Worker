import pathlib
from typing import List

from dagster import get_dagster_logger
from pydantic import (
    Field,
)

LOGGER = get_dagster_logger(__name__)

from OpenStudioLandscapes.engine.config.str_gen import get_config_str
from OpenStudioLandscapes.engine.config.models import FeatureBaseModel

from OpenStudioLandscapes.Deadline_10_2_Worker import dist, constants


class Config(FeatureBaseModel):
    feature_name: str = dist.name

    group_name: str = constants.ASSET_HEADER["group_name"]

    key_prefixes: List[str] = constants.ASSET_HEADER["key_prefix"]

    enabled: bool = Field(
        default=False,
        description="# Not enabled by default because this Feature has some basic requirements, such as the installers."
    )

    compose_scope: str = "worker"

    deadline_10_2_worker_PADDING: int = Field(
        default=3,
    )

    deadline_10_2_worker_NUM_SERVICES: int = Field(
        default=1,
        description="Number of workers to simulate in parallel.",
    )

    deadline_10_2__worker_storage: pathlib.Path = Field(
        default=pathlib.Path("{DOT_LANDSCAPES}/{LANDSCAPE}/{FEATURE}/storage"),
    )

    # EXPANDABLE PATHS
    @property
    def deadline_10_2__worker_storage_expanded(self) -> pathlib.Path:
        LOGGER.debug(f"{self.env = }")
        if self.env is None:
            raise KeyError("`env` is `None`.")
        LOGGER.debug(f"Expanding {self.deadline_10_2__worker_storage}...")
        ret = pathlib.Path(
            self.deadline_10_2__worker_storage.expanduser()
            .as_posix()
            .format(
                **{
                    "FEATURE": self.feature_name,
                    **self.env,
                }
            )
        )
        return ret


CONFIG_STR = get_config_str(
    Config=Config,
)

