from fractions import Fraction
from inspect import cleandoc
import unittest

from pyexpect import expect

from cooklang import Ingredient, Quantity, Recipe, Timer


class ParserTest(unittest.TestCase):
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
                Ingredient("stuff"),
                Ingredient("other things"),
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

            Use @salt{0.5%grams} and @amaranth{1/2%cup}
        """  # noqa: E501
            )
        )
        expect(recipe.metadata).to_equal({})
        expect(recipe.ingredients).to_equal(
            [
                Ingredient("sugar", Quantity(42, "grams")),
                Ingredient("green onions", Quantity(10, "grams")),
                Ingredient("salt", Quantity(0.5, "grams")),
                Ingredient("amaranth", Quantity(Fraction(1, 2), "cup")),
            ]
        )
        expect(recipe.steps).to_equal(
            [
                "Place sugar in the pan along with green onions",
                "Use salt and amaranth",
            ]
        )

    def test_adding_up_ingredient_quantities(self) -> None:
        recipe = Recipe.parse(
            cleandoc(
                """
            Add @salt{0.1%grams} and @salt{0.2%grams}. Add more @salt to taste

            Add @amaranth{1/2%cup} and @amaranth{1/4%cup}.

            Add @butter{1%cup} and @butter{2%cup}.

            Pour some @olive oil{}

            Add @garlic{1}
        """  # noqa: E501
            )
        )
        expect(recipe.ingredients).to_equal(
            [
                Ingredient("salt", Quantity(0.3, "grams")),
                Ingredient("amaranth", Quantity(Fraction(3, 4), "cup")),
                Ingredient("butter", Quantity(3, "cup")),
                Ingredient("olive oil"),
                Ingredient("garlic", Quantity(1)),
            ]
        )

    def test_more_complex_ingredient_extraction(self) -> None:
        recipe = Recipe.parse(
            cleandoc(
                """
            Put @green olives{5%units} in the #big bowl{}, together with @salt{2%grams} and @green onions{}

            Season with @salt and @pepper.

            Get the @sauté vegetables{}.
        """  # noqa: E501
            )
        )
        expect(recipe.metadata).to_equal({})
        expect(recipe.ingredients).to_equal(
            [
                Ingredient("green olives", Quantity(5, "units")),
                Ingredient("salt", Quantity(2, "grams")),
                Ingredient("green onions"),
                Ingredient("pepper"),
                Ingredient("sauté vegetables"),
            ]
        )
        expect(recipe.steps).to_equal(
            [
                "Put green olives in the big bowl, together with salt and green onions",  # noqa: E501
                "Season with salt and pepper.",
                "Get the sauté vegetables.",
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

    def test_stripping_out_comments(self) -> None:
        recipe = Recipe.parse(
            cleandoc(
                """
            -- comments can be added anywhere
            >> time: 15 mins -- even here!

            -- before paragraphs too
            Hey this is a paragraph with no ingredients
            -- after them too
            Another paragraph!

            [- block comment here -]
            and [- in text somewhere -]
            as well
        """
            )
        )
        expect(recipe.metadata).to_equal({"time": "15 mins"})
        expect(recipe.ingredients).to_equal([])
        expect(recipe.steps).to_equal(
            [
                "Hey this is a paragraph with no ingredients",
                "Another paragraph!",
                "and",
                "as well",
            ]
        )

    def test_stripping_out_timing(self) -> None:
        recipe = Recipe.parse(
            cleandoc(
                """
            Cook the @pasta for ~{10%minutes}
        """
            )
        )
        expect(recipe.metadata).to_equal({})
        expect(recipe.ingredients).to_equal(
            [
                Ingredient("pasta"),
            ]
        )
        expect(recipe.steps).to_equal(
            [
                "Cook the pasta for 10 minutes",
            ]
        )

    def test_skip_invalid_syntax(self) -> None:
        recipe = Recipe.parse(
            cleandoc(
                """
            # For instance, a markdown header

            @ Or something else here

            ~ Or this
        """
            )
        )
        expect(recipe.metadata).to_equal({})
        expect(recipe.ingredients).to_equal([])
        expect(recipe.steps).to_equal(
            [
                "# For instance, a markdown header",
                "@ Or something else here",
                "~ Or this",
            ]
        )

    def test_cookware_extraction(self) -> None:
        recipe = Recipe.parse(
            cleandoc(
                """
            Place stuff in the #pan

            Place other things in the #large bowl{}
        """
            )
        )
        expect(recipe.metadata).to_equal({})
        expect(recipe.cookware).to_equal(
            [
                "pan",
                "large bowl",
            ]
        )
        expect(recipe.ingredients).to_equal([])
        expect(recipe.steps).to_equal(
            [
                "Place stuff in the pan",
                "Place other things in the large bowl",
            ]
        )

    def test_timer_extraction(self) -> None:
        recipe = Recipe.parse(
            cleandoc(
                """
            Cook in oven for ~quiche{30%minutes}

            Let cool for ~{1%hour}
        """
            )
        )
        expect(recipe.metadata).to_equal({})
        expect(recipe.cookware).to_equal([])
        expect(recipe.ingredients).to_equal([])
        expect(recipe.timers).to_equal(
            [
                Timer("quiche", Quantity(30, "minutes")),
                Timer("", Quantity(1, "hour")),
            ]
        )
        expect(recipe.steps).to_equal(
            [
                "Cook in oven for 30 minutes",
                "Let cool for 1 hour",
            ]
        )


if __name__ == "__main__":
    unittest.main()
