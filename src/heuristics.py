from .map import GameMap
import random

def evaluate_game_state(map: GameMap):
    """
    Evaluate the game state with dynamic weights and a high initial attack focus
    """
    our_position, our_units = map.get_biggest_position()
    opponent_position, opponent_units = map.get_enemy_biggest_position()

    # Edge cases: game win or loss
    if type(our_position) is int:
        return -100000  # Loss condition
    if type(opponent_position) is int:
        return 100000  # Win condition

    # Dynamic proximity based on grid size
    proximity = max(map.get_grid_size()) // 3

    # Fixed coefficients with dynamic adjustments
    attack_coef = 100 if our_units + opponent_units < sum(map.humans_state.values()) // 2 else 50
    resource_coef = 1 if attack_coef == 100 else 2


    our_resource_gain = calculate_resource_gain(our_position, our_units, map.humans_state, proximity)
    opponent_resource_gain = calculate_resource_gain(opponent_position, opponent_units, map.humans_state, proximity)
    our_attack_power = calculate_attack_power(our_position, our_units, map.get_enemy_dict(), proximity)
    distance_penalty_score = -0.5 * distance_penalty(our_position, opponent_position)

    resource_diff = resource_coef * (our_resource_gain - opponent_resource_gain)
    attack_score = attack_coef * our_attack_power
    unit_difference = 10 * (our_units - opponent_units)


    return unit_difference + resource_diff + attack_score + distance_penalty_score + random.uniform(0, 0.01)

def calculate_resource_gain(position, units, humans_states, proximity):
    """
    Calculate potential resource gain by converting humans within a given proximity
    """
    max_gain = 0
    x, y = position

    for i in range(-proximity, proximity + 1):
        for j in range(-proximity, proximity + 1):
            target_pos = (x + i, y + j)
            if target_pos in humans_states:
                human_count = humans_states[target_pos]
                if human_count <= units:  # Check if we can convert them
                    distance = max(abs(i), abs(j))
                    efficiency = human_count / distance
                    max_gain = max(max_gain, efficiency)
    return max_gain

def calculate_attack_power(position, units, enemy_dict, proximity):
    """
    Calculate potential attack power by defeating enemies within a given proximity
    """
    max_power = 0
    x, y = position

    for i in range(-proximity, proximity + 1):
        for j in range(-proximity, proximity + 1):
            target_pos = (x + i, y + j)
            if target_pos in enemy_dict:
                enemy_count = enemy_dict[target_pos]
                if enemy_count < units:  # Check if we can attack them
                    distance = max(abs(i), abs(j))
                    efficiency = enemy_count / distance
                    max_power = max(max_power, efficiency)
    return max_power

def distance_penalty(current_pos, target_pos):
    """
    Calculate a penalty based on the Manhattan distance between two positions
    """
    x1, y1 = current_pos
    x2, y2 = target_pos
    return abs(x1 - x2) + abs(y1 - y2)
