import itertools
import re
from dataclasses import dataclass
from typing import Mapping, Sequence, Union


@dataclass
class Ingredient:
    name: str
    amount: Union[int, float]
    unit: str

    @classmethod
    def parse(cls, raw: str) -> "Ingredient":
        name, raw_amount = re.findall(r"^@([^{]+)(?:{([^}]*)})?", raw)[0]
        matches = re.findall(r"([^%]+)%([a-z]+)", raw_amount)
        amount = 1
        unit = "units"
        if matches:
            matches = matches[0]
            # TODO support floats
            amount = int(matches[0]) if matches[0] else 1
            unit = str(matches[1]) if matches[1] else "units"
        return Ingredient(
            name=name,
            amount=amount,
            unit=unit,
        )


@dataclass
class Recipe:
    metadata: Mapping[str, str]
    ingredients: Sequence[Ingredient]
    steps: Sequence[str]

    @classmethod
    def parse(cls, raw: str) -> "Recipe":
        raw_steps = list(filter(None, raw.split("\n\n")))
        ingredients = list(
            itertools.chain(
                *map(
                    lambda raw_step: list(
                        map(
                            lambda s: Ingredient.parse(s),
                            re.findall(
                                r"@(?:(?:[^{]+?){[^}]*}|[A-Za-z]+)",
                                raw_step,
                            ),
                        )
                    ),
                    raw_steps,
                )
            )
        )
        return Recipe(metadata={}, ingredients=ingredients, steps=raw_steps)
