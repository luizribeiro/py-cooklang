from inspect import cleandoc
from unittest import TestCase

from pyexpect import expect

from cooklang import Ingredient, Recipe


class ParserTest(TestCase):
    def test_empty_file(self) -> None:
        recipe = Recipe.parse("")
        expect(recipe.metadata).to_equal({})
        expect(recipe.ingredients).to_equal([])
        expect(recipe.steps).to_equal([])

    def test_basic_recipe(self) -> None:
        recipe = Recipe.parse(
            cleandoc(
                """
            Place @stuff in the pan

            Place @other things{} in the pan too
        """
            )
        )
        expect(recipe.metadata).to_equal({})
        expect(recipe.ingredients).to_equal(
            [
                Ingredient("stuff", 1, "units"),
                Ingredient("other things", 1, "units"),
            ]
        )
        expect(recipe.steps).to_equal(
            [
                "Place @stuff in the pan",
                "Place @other things{} in the pan too",
            ]
        )
