from unittest import TestCase

from pyexpect import expect

from cooklang import Recipe


class ParserTest(TestCase):
    def test_empty_file(self) -> None:
        recipe = Recipe.parse("")
        expect(recipe.metadata).to_equal({})
        expect(recipe.ingredients).to_equal([])
        expect(recipe.steps).to_equal([])
