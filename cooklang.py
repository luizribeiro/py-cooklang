import itertools
import re
from dataclasses import dataclass
from typing import Mapping, Optional, Sequence, Tuple, Union


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
        raw_without_comments = re.sub(r"//[^\n]+", "", raw)
        raw_paragraphs = list(
            filter(None, map(str.strip, raw_without_comments.split("\n")))
        )

        raw_steps = list(
            filter(
                lambda x: not x.startswith(">>"),
                raw_paragraphs,
            )
        )
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

        def _extract_metadata(raw_line: str) -> Optional[Tuple[str, str]]:
            res = re.search(r"^>> ?([^:]+): ?(.*)$", raw_line)
            if not res:
                return None
            return (res.group(1).strip(), res.group(2).strip())

        raw_metadata = list(
            filter(
                lambda x: x.startswith(">>"),
                raw_paragraphs,
            )
        )
        metadata = dict(
            filter(
                None,
                (_extract_metadata(raw_line) for raw_line in raw_metadata),
            )
        )

        return Recipe(
            metadata=metadata,
            ingredients=ingredients,
            steps=[
                re.sub(
                    r"(?:@|#)([^{]+)({[^}]*})?",
                    r"\1",
                    raw_step,
                )
                for raw_step in raw_steps
            ],
        )
