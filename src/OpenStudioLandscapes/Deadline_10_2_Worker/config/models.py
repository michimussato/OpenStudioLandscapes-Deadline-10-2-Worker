import pathlib

from dagster import get_dagster_logger
from pydantic import (
    Field,
)

LOGGER = get_dagster_logger(__name__)

from OpenStudioLandscapes.engine.config.models import FeatureBaseModel

from OpenStudioLandscapes.Deadline_10_2_Worker import dist

config_default = pathlib.Path(__file__).parent.joinpath("config_default.yml")
CONFIG_STR = config_default.read_text()


class Config(FeatureBaseModel):
    feature_name: str = dist.name

    definitions: str = "OpenStudioLandscapes.Deadline_10_2_Worker.definitions"

    enabled: bool = False

    compose_scope: str = "worker"

    deadline_10_2_worker_PADDING: int = Field(
        default=3,
    )

    deadline_10_2_worker_NUM_SERVICES: int = Field(
        default=5,
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
