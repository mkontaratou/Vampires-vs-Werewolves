import numpy as np
from copy import deepcopy
import math

class GameMap:
    def __init__(self, map_height, map_width, map_state, init_pos):
        # states are going to be a dictionary of tuple keys containing position and value of the number (x, y): nb_species
        self.humans_state = {}
        self.vamps_state = {}
        self.wolves_state = {}
        self.grid_size = np.array([map_height, map_width])
        self.is_vampire = None  # Our type

        self.init_map(map_state, init_pos)

    def init_map(self, map_state, init_pos):
        for position in map_state:
            # is human
            if position[2]:
                self.humans_state[(position[0], position[1])] = position[2]
            # is vamps
            elif position[3]:
                self.vamps_state[(position[0], position[1])] = position[3]

                if (init_pos[0] == position[0]) and (init_pos[1] == position[1]):
                    self.is_vampire = True
            # is wolves
            elif position[4]:
                self.wolves_state[(position[0], position[1])] = position[4]

                if (init_pos[0] == position[0]) and (init_pos[1] == position[1]):
                    self.is_vampire = False

    def update_map(self, updates):
        for position in updates:

            if position[2] == 0:  # erase human position if exist
                self.humans_state.pop((position[0], position[1]), -1)
            else:  # set the value (insert or update)
                self.humans_state[(position[0], position[1])] = position[2]

            if position[3] == 0:  # erase vampires position if exist
                self.vamps_state.pop((position[0], position[1]), -1)
            else:  # set the value (insert or update)
                self.vamps_state[(position[0], position[1])] = position[3]

            if position[4] == 0:  # erase werewolves position if exist
                self.wolves_state.pop((position[0], position[1]), -1)
            else:  # set the value (insert or update)
                self.wolves_state[(position[0], position[1])] = position[4]

    def get_current_pos(self):
        if self.is_vampire:
            return list(self.vamps_state.keys())
        return list(self.wolves_state.keys())

    def get_enemy_pos(self):
        if self.is_vampire:
            return list(self.wolves_state.keys())
        return list(self.vamps_state.keys())

    def get_my_count(self):
        if self.is_vampire:
            return list(self.vamps_state.values())
        return list(self.wolves_state.values())

    def get_enemy_count(self):
        if self.is_vampire:
            return list(self.wolves_state.values())
        return list(self.vamps_state.values())

    def get_enemy_dict(self):
        # Return the number of opponents at each position they occupy
        if self.is_vampire:
            return self.wolves_state
        return self.vamps_state

    def get_current_element(self):
        # TODO: not adapted for splitting
        x, y = self.get_current_pos()[0]
        if self.is_vampire:
            return (x, y), self.vamps_state[x, y]
        return (x, y), self.wolves_state[x, y]

    # TODO find ways to remove this (needs to be removed from PossibleMoves)
    def get_grid_size(self):
        return self.grid_size


    def display_state(self):
        print("---- HUMANS ----\n", self.humans_state)
        print("---- VAMPS ----n", self.vamps_state)
        print("---- WOLVES ----\n", self.wolves_state)

        
        
    def update_enemy_state(self, x, y, nb):
        if self.is_vampire:
            nb_enemy = self.wolves_state[(x, y)] = nb
        else:
            nb_enemy = self.vamps_state[(x, y)] = nb

        return nb_enemy

    def remove_enemy_state(self, x, y):
        if self.is_vampire:
            nb_enemy = self.wolves_state.pop((x, y), 0)
        else:
            nb_enemy = self.vamps_state.pop((x, y), 0)

        return nb_enemy

    def remove_my_state(self, x, y):
        if self.is_vampire:
            self.vamps_state.pop((x, y), -1)
        else:
            self.wolves_state.pop((x, y), -1)

    def update_my_state(self, x, y, nb):
        if self.is_vampire:
            self.vamps_state[(x, y)] = nb
        else:
            self.wolves_state[(x, y)] = nb

    def get_biggest_position(self):
        nb_units = self.get_my_count()

        if not nb_units:
            return 0, 0

        index = np.argmax(self.get_my_count())

        return self.get_current_pos()[index], self.get_my_count()[index]

    def get_enemy_biggest_position(self):
        nb_enemies = self.get_enemy_count()

        if not nb_enemies:
            return 0, 0
        index = np.argmax(self.get_enemy_count())

        return self.get_enemy_pos()[index], self.get_enemy_count()[index]

    def possible_moves(self):
        positions = []
        # Question for later: Why use the biggest move
        current_pos, current_nb = self.get_biggest_position()
        x, y = current_pos

        for i in range(max(0, x-1), min(self.grid_size[1], x+2)):
            for j in range(max(0, y-1), min(self.grid_size[0], y+2)):
                if self.is_guaranteed_win(i, j):
                    positions.append([i, j, current_nb])
        positions.remove([x, y, current_nb])
        return positions

    def is_guaranteed_win(self, x, y):
        current_pos, current_nb = self.get_biggest_position()

        nb_humans = self.humans_state.get((x, y), 0)

        if self.is_vampire:
            nb_enemy = self.wolves_state.get((x, y), 0)
        else:
            nb_enemy = self.vamps_state.get((x, y), 0)

        if nb_humans > 0:
            if current_nb >= nb_humans:
                return True
            return False

        if nb_enemy > 0:
            if current_nb > 1.5 * nb_enemy:
                return True
            return False
        return True


    


    def _simulate_move(self, x, y, nb_units):

        ####### INIT POS ########
        # We remove ourselves from the init pos
        if nb_units == 0:
            self.remove_my_state(x, y)
            return

        ####### TARGET POS ########

        # If humans are in target position remove them and get their number
        nb_humans = self.humans_state.pop((x, y), 0)

        # If enemies are in target position remove them and get their number
        nb_enemy = self.remove_enemy_state(x, y)

        if nb_humans > 0:
            outcome = battle_humans(nb_units, nb_humans)

            if outcome > 0:
                self.update_my_state(x, y, outcome)
            else:
                self.humansPos[(x, y)] = nb_humans

        elif nb_enemy > 0:  # we need to simulate a fight
            proba, outcome = battle_enemy(nb_units, nb_enemy)

            if outcome > 0:
                self.update_my_state(x, y, outcome)
            else:
                enemy_survived = approx_nb_surviving_attacked(nb_enemy, proba)
                self.update_enemy_state(x, y, enemy_survived)
        else:
            self.update_my_state(x, y, nb_units)


    def generate_updated_map(self, final_pos):
        # Generates a new map with updated position
        # input: final_position
        # output: generated map copy

        current_pos, current_nb = self.get_current_element()

        # generate a new board
        new_board = deepcopy(self)

        # update current position
        new_board._simulate_move(current_pos[0], current_pos[1], 0)

        # update target position
        new_board._simulate_move(final_pos[0], final_pos[1], current_nb)

        return new_board


####### BATTLE MODE AND RANDOM BATTLE ########
def calculate_small_attacker_probability(e1: int, e2: int) -> float:

    return e1 / (2 * e2)

def calculate_large_attacker_probability(e1: int, e2: int) -> float:
    return e1 / e2 - 0.5

def approximate_winning_attackers(e1: int, e2: int, proba: float) -> int:
    return math.floor((e1 + e2) * proba)

def approximate_surviving_defenders(e2: int, proba: float) -> int:
    return math.floor(e2 * (1 - proba))

def battle_humans(attacker_units: int, human_units: int) -> int:
    """
    Simulate a battle between attackers and humans.
    
    Parameters:
    - attacker_units: Number of attacking units.
    - human_units: Number of human defenders.
    
    Returns:
    - Approximate number of attackers remaining after the battle.
    """
    if attacker_units >= human_units:
        probability = 1  # Guaranteed win
    else:  # Random battle
        probability = calculate_small_attacker_probability(attacker_units, human_units)

    return approximate_winning_attackers(attacker_units, human_units, probability)

def battle_enemy(attacker_units: int, enemy_units: int) -> tuple:
    """
    Simulate a battle between attackers and enemies.
    
    Parameters:
    - attacker_units: Number of attacking units.
    - enemy_units: Number of defending enemy units.
    
    Returns:
    - probability: Probability of the attackers winning.
    - remaining_attackers: Approximate number of attackers remaining after the battle.
    """
    if attacker_units > enemy_units:
        probability = 1  # Guaranteed win
    else:
        probability = 0  # Guaranteed loss 

    remaining_attackers = approximate_winning_attackers(attacker_units, enemy_units, probability)
    return probability, remaining_attackers

####### END BATTLE MODE AND RANDOM BATTLE ########