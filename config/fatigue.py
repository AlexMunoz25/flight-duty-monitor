import tomllib
from dataclasses import dataclass
from pathlib import Path

CONFIG_PATH = Path(__file__).with_name("fatigue.toml")


@dataclass(frozen=True)
class FatigueConfig:
    low_alertness_threshold: int
    weekly_block_limit_hours: int
    rolling_window: str


def load_fatigue_config(path=CONFIG_PATH):
    fatigue = tomllib.loads(path.read_text())["fatigue"]
    return FatigueConfig(
        low_alertness_threshold=fatigue["low_alertness_threshold"],
        weekly_block_limit_hours=fatigue["weekly_block_limit_hours"],
        rolling_window=fatigue["rolling_window"],
    )


FATIGUE_CONFIG = load_fatigue_config()
