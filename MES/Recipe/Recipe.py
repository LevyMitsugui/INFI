import csv


class Recipe(object):
    def __init__(self, filename='Recipe/recipes.csv'):
        """
        Initializes a new instance of the class with an optional filename parameter.

        Parameters:
            filename (str): The name of the file to be used for storing recipes. Defaults to 'Recipe/recipes.csv'.

        Returns:
            None
        """
        self.filename = filename

    def getRecipeData(self, name):
        with open(self.filename, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['Piece'] == name:
                    return row

    def getRecipes(self, name):
        recipes = []
        with open(self.filename, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['Piece'] == name:
                    recipes.append((float(row['Time']), row['Material'], row['Tools'].split(';')))
        return recipes
    
def getRecipes(filename, name):
        recipes = []
        with open(filename, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['Piece'] == name:
                    recipes.append((float(row['Time']), row['Material'], row['Tools'].split(';')))
        return recipes

