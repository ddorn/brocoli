from abc import ABC, abstractmethod
from random import random, choice


class GeneticAlgorithm(ABC):
    KEEP_BEST = 0.05
    """Every individual in the top KEEP_BEST 
    proportion will be taken unmodified for the next generation"""
    KEEP_PARENTS = 0.2
    """Every individual in the top KEEP_PARENTS proportion
    will be used for the next generation through crossovers"""

    def __init__(self, population):
        self.pop_size = population
        self.population = self.create_population(population)
        self.iteration = 0

    @abstractmethod
    def random_individual(self):
        ...

    @abstractmethod
    def crossover(self, girl, guy):
        ...

    @abstractmethod
    def mutate(self, girl):
        ...

    @abstractmethod
    def judge(self, guy):
        ...

    def choose_parents(self):
        """Choose parents in the sorted population."""
        # elites_thresold = int(self.KEEP_BEST * len(graded))
        parents_thresold = int(self.KEEP_PARENTS * len(graded))
        # elites = graded[:elites_thresold]
        parents = self.population[:parents_thresold]
        return parents

    def crossover_all(self, parents):
        new = [
            self.crossover(choice(parents), choice(parents))
            for _ in range(self.pop_size)
        ]
        return new

    def create_population(self, total):
        return [self.random_individual() for _ in total]

    def mutate_all(self, pop):
        return [self.mutate(guy) for guy in pop]

    def sort(self):
        self.population.sort(key=self.judge, reverse=True)

    def evolve(self):
        parents = self.choose_parents()
        children = self.crossover_all(parents)
        self.population = self.mutate_all(children)
        self.sort()
        self.iteration += 1

    def run(self, generations):
        for _ in range(generations):
            self.evolve()
            print(f"*** Generation {self.iteration} ***")
            for i in range(5):
                print("Best", i, ":", self.population[i])


class GradientGA(GeneticAlgorithm):
    LENGTH = 4

    def random_individual(self):
        return tuple((random(), random(), random()) for _ in range(self.LENGTH))

    def crossover(self, girl, guy):
        pass

    def mutate_one(self, girl):
        pass

    def judge(self, guy):
        pass
