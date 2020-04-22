from abc import ABC, abstractmethod
from colorsys import hsv_to_rgb
from math import sin, cos, tau
from random import random, choice, randint, randrange
from time import time

try:
    from .colors import gradient
except ImportError:
    from colors import gradient


def clamp(x, mini=0, maxi=1):
    if x < mini:
        return mini
    elif x > maxi:
        return maxi
    return x


def hsvdist(c1, c2):
    h1, s1, v1 = c1
    h2, s2, v2 = c2

    return (
        (sin(h1 * tau) * s1 * v1 - sin(h2 * tau) * s2 * v2) ** 2
        + (cos(h1 * tau) * s1 * v1 - cos(h2 * tau) * s2 * v2) ** 2
        + (v1 - v2) ** 2
    )


def itercols(grad):
    for i in range(0, len(grad), 3):
        yield grad[i : i + 3]


def rgb_to_hex(rgb):
    return "#" + "".join("0" * (c < 1 / 16) + hex(int(round(c * 255)))[2:] for c in rgb)


def hsv_to_RGB(hsv):
    rgb = hsv_to_rgb(*hsv)
    return [int(round(255 * c)) for c in rgb]


def pretty(hsv):
    rgb = hsv_to_RGB(hsv)
    hsv = [int(c * 100) for c in hsv]
    s = "\033[48;2;{};{};{}m{:02}-{:02}-{:02}\033[m".format(*rgb, *hsv)
    return s


def bg(text, rgb):
    return "\033[48;2;{};{};{}m".format(*rgb) + text


def fg(text, rgb):
    return "\033[38;2;{};{};{}m".format(*rgb) + text


def gradient_str(grad, size=100):
    text = [
        "{:02}-{:02}-{:02}".format(*[int(x * 100) for x in c]) for c in itercols(grad)
    ]
    total_len = sum(map(len, text))
    space = int((size - total_len) / (len(text) - 1))
    text = (" " * space).join(text)
    text += " " * (size - len((text)))

    grad = [hsv_to_RGB(grad[i : i + 3]) for i in range(0, len(grad), 3)]
    grad = list(gradient(*grad, steps=size))

    s = "".join(
        bg(fg(c, (50 if sum(g) > 300 else 200,) * 3), g) for g, c in zip(grad, text)
    )
    s = bg("   ", grad[0]) + s + bg("   ", grad[-1]) + "\033[m"
    return s


class GeneticAlgorithm(ABC):
    KEEP_BEST = 0.05
    """Every individual in the top KEEP_BEST 
    proportion will be taken unmodified for the next generation"""
    KEEP_PARENTS = 0.5
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
        parents_thresold = int(self.KEEP_PARENTS * len(self.population))
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
        return [self.random_individual() for _ in range(total)]

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
            print("Worst:", self.population[-1])


class GradientGA(GeneticAlgorithm):
    LENGTH = 4
    SWAP_MUTATION = 0.2
    """Probability that a mutation swaps two colors"""
    CHANGE_MUTATION = 0.8
    MUTATION_AMPLITUDE = 0.2

    def random_individual(self):
        return [random() for _ in range(self.LENGTH * 3)]

    def crossover(self, girl, guy):
        sep = randrange(len(girl) // 3) * 3
        return girl[:sep] + guy[sep:]

    def mutate(self, girl):

        if random() < self.SWAP_MUTATION:
            a = randrange(len(girl) // 3) * 3
            b = randrange(len(girl) // 3) * 3
            girl[a : a + 3], girl[b : b + 3] = girl[b : b + 3], girl[a : a + 3]
        else:
            idx = randrange(len(girl))
            a = girl[idx]
            var = (random() * 2 - 1) * self.MUTATION_AMPLITUDE
            if idx % 3 == 0:
                # rotate hue
                girl[idx] = (a + var) % 1
            else:
                # shift saturation / value
                girl[idx] = clamp(a + var)

        return girl

    def judge(self, guy):
        score = 0
        length = len(guy) // 3
        # Penalise similar colors

        similar = 0
        for i in range(0, len(guy), 3):
            for j in range(0, len(guy), 3):
                if i == j:
                    continue
                if hsvdist(guy[i : i + 3], guy[j : j + 3]) < 0.3:
                    similar += 1
        score += -similar / length

        # Encourage saturation
        sat = sum(guy[1::3]) / length
        if sat > 0.8:
            score += 0.5
        elif sat > 0.6:
            score += 1

        # Encourage one orange
        orange = 0
        for c in itercols(guy):
            if 0.05 < c[0] < 0.15 and c[1] > 0.8 and c[2] > 0.85:
                orange = max(0.05 - abs(c[0] - 0.1), orange)
        score += orange * 0

        # Penalise grayish colors
        grayish = 0
        for c in itercols(guy):
            if c[1] < 0.3 and c[2] < 0.3:
                grayish += c[1] + c[2]
        score -= grayish

        return score

    def run(self, generations, show=False):
        for _ in range(generations):
            self.evolve()
            if show:
                print(f"*** Generation {self.iteration} ***")
                for i in range(5):
                    print(gradient_str(self.population[i]))
                print("Worst:", gradient_str(self.population[-1]))

        if show:
            scores = list(map(self.judge, self.population))
            for i in reversed(range(len(self.population))):
                print(i, round(scores[i], 2), gradient_str(self.population[i]))

    def best_RGB(self):
        return [hsv_to_RGB(c) for c in itercols(self.population[0])]


if __name__ == "__main__":
    t = time()
    ga = GradientGA(50)
    ga.run(30, True)
    print(time() - t)
