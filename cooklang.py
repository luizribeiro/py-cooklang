from dataclasses import dataclass
from typing import Mapping, Sequence, Union


@dataclass
class Quantity:
    amount: Union[int, float]
    unit: str


@dataclass
class Recipe:
    metadata: Mapping[str, str]
    ingredients: Sequence[Quantity]
    steps: Sequence[str]

    @classmethod
    def parse(cls, raw: str) -> "Recipe":
        return Recipe(metadata={}, ingredients=[], steps=[])
