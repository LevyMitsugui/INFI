import unittest
import Recipe

class testRecipe(unittest.TestCase):
    def test_getRecipes(self):
        recipe = Recipe.Recipe()
        recipes = recipe.getRecipes('P5')
        self.assertEqual(recipes, [(85.0, 'P1', ['T1', 'T2', 'T4']), (95.0, 'P1', ['T1', 'T3', 'T4'])])

if __name__ == '__main__':
    unittest.main()