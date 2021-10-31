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

    def test_ingredient_name_extraction(self) -> None:
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
                "Place stuff in the pan",
                "Place other things in the pan too",
            ]
        )

    def test_ingredient_quantity_extraction(self) -> None:
        recipe = Recipe.parse(
            cleandoc(
                """
            Place @sugar{42%grams} in the pan along with @green onions{10%grams}
        """
            )
        )
        expect(recipe.metadata).to_equal({})
        expect(recipe.ingredients).to_equal(
            [
                Ingredient("sugar", 42, "grams"),
                Ingredient("green onions", 10, "grams"),
            ]
        )
        expect(recipe.steps).to_equal(
            [
                "Place sugar in the pan along with green onions",
            ]
        )

    def test_metadata_extraction(self) -> None:
        recipe = Recipe.parse(
            cleandoc(
                """
            >> time: 15 mins
            >> course: lunch, dinner
            >> servings: 4|2|1
            >>  weird spacing  :   every where
        """
            )
        )
        expect(recipe.metadata).to_equal(
            {
                "time": "15 mins",
                "course": "lunch, dinner",
                "servings": "4|2|1",
                "weird spacing": "every where",
            }
        )
        expect(recipe.ingredients).to_equal([])
        expect(recipe.steps).to_equal([])
