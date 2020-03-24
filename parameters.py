# -----------------------------------------------------------
# This module represents a parameters object for the genetic algorithm.
#
# Parameters include:
# (1) population_size       (number of chromosomes in a single generation)
# (2) maximum_generations   (number of generations after which execution stops)
# (3) mutation_rate         (probability of a mutation occurring)
# (4) mutation_size         (lectures disturbed in a single mutation)
# (5) crossover_rate        (probability of a crossover occurring)
# (6) crossover_size        (skew of copying information from parents)
# (7) week_days             (number of days University is open)
# (8) daily_hours           (number of hours University is open)
#
#
# (C) 2020 PyShoaib
# -----------------------------------------------------------


class Parameters:
    '''
    Defines GA parameters.
    '''
    def __init__(
        self,
        population_size: int=60,
        maximum_generations: int=1000,
        mutation_rate: float=0.05,
        mutation_size: float=0.10,
        crossover_rate: float=0.80,
        crossover_size: float=0.50,
        week_days: int=5,
        daily_hours: int=8
        ):
        self.population_size = population_size
        self.maximum_generations = maximum_generations
        self.mutation_rate = mutation_rate
        self.mutation_size = mutation_size
        self.crossover_rate = crossover_rate
        self.crossover_size = crossover_size
        self.week_days = week_days
        self.daily_hours = daily_hours

    
    def __repr__(self):
        return(
            f'Population Size: {self.population_size}\n'
            f'Maximum Generations: {self.maximum_generations}\n'
            f'Mutation Rate: {self.mutation_rate}\n'
            f'Mutation Size: {self.mutation_size}\n'
            f'Crossover Rate: {self.crossover_rate}\n'
            f'Crossover Size: {self.crossover_size}\n'
            f'Weekdays: {self.week_days}\n'
            f'Daily hours: {self.daily_hours}\n'
        )