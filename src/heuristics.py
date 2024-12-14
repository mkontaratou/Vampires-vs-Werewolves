from .map import GameMap
import random


def evaluate_game_state(map: GameMap):
    """
    Evaluate the game state with dynamic weights and strategic positionings
    """
    our_position, our_units = map.get_biggest_position()
    opponent_position, opponent_units = map.get_enemy_biggest_position()

    # Edge cases: game win or loss
    if type(our_position) is int:
        return -100000  # Loss condition
    if type(opponent_position) is int:
        return 100000  # Win condition

    # Dynamic range based on grid size
    range_limit = max(map.get_grid_size()) // 3

    # Dynamic weight adjustments
    total_units = our_units + opponent_units
    total_humans = sum(map.humans_state.values())
    progress_ratio = total_units / (total_units + total_humans)  # Early vs. Late game indicator

    # Adjust coefficients dynamically
    attack_coef = 100 if progress_ratio < 0.5 else 70  # Prioritize attacking early
    resource_coef = 10 if progress_ratio < 0.5 else 20  # Prioritize humans later
    distance_penalty_coef = -0.5

    # Strategic Positioning
    strategic_positioning_score = calculate_strategic_positioning(our_position, opponent_position, range_limit)

    # Calculate heuristic components
    our_resource_gain = calculate_resource_gain(our_position, our_units, map.humans_state, range_limit)
    opponent_resource_gain = calculate_resource_gain(opponent_position, opponent_units, map.humans_state, range_limit)
    our_attack_power = calculate_attack_power(our_position, our_units, map.get_enemy_dict(), range_limit)
    distance_penalty_score = distance_penalty_coef * distance_penalty(our_position, opponent_position)

    resource_gain_difference = resource_coef * (our_resource_gain - opponent_resource_gain)
    attack_score = attack_coef * our_attack_power
    advantage_units = 10 * (our_units - opponent_units)

    # Improved random bias for tie-breaking
    random_bias = random.uniform(-0.1, 0.1)

    return (
        advantage_units
        + resource_gain_difference
        + attack_score
        + strategic_positioning_score
        + distance_penalty_score
        + random_bias
    )


def calculate_resource_gain(position, units, humans_states, range_limit):
    """
    Calculate potential resource gain by converting humans within a given range
    """
    max_gain = 0
    x, y = position

    for i in range(-range_limit, range_limit + 1):
        for j in range(-range_limit, range_limit + 1):
            target_pos = (x + i, y + j)
            if target_pos in humans_states:
                human_count = humans_states[target_pos]
                if human_count <= units:  # Check if we can convert them
                    distance = max(abs(i), abs(j))
                    efficiency = human_count / distance
                    max_gain = max(max_gain, efficiency)
    return max_gain


def calculate_attack_power(position, units, enemy_dict, range_limit):
    """
    Calculate potential attack power by defeating enemies within a given range.
    """
    max_power = 0
    x, y = position

    for i in range(-range_limit, range_limit + 1):
        for j in range(-range_limit, range_limit + 1):
            target_pos = (x + i, y + j)
            if target_pos in enemy_dict:
                enemy_count = enemy_dict[target_pos]
                if enemy_count < units:  # Check if we can attack them
                    distance = max(abs(i), abs(j))
                    efficiency = enemy_count / distance
                    max_power = max(max_power, efficiency)
    return max_power


def calculate_strategic_positioning(our_position, opponent_position, range_limit):
    """
    Calculate a bonus score for positioning relative to the opponent
    """
    x1, y1 = our_position
    x2, y2 = opponent_position

    distance = max(abs(x1 - x2), abs(y1 - y2))  # Use Chebyshev distance
    if distance <= range_limit:
        # Encourage being close to opponents (but not too close)
        return 50 / (distance + 1)
    else:
        return -10  # Penalize being too far away


def distance_penalty(current_pos, target_pos):
    """
    Calculate a penalty based on the Manhattan distance between two positions
    """
    x1, y1 = current_pos
    x2, y2 = target_pos
    return abs(x1 - x2) + abs(y1 - y2)
