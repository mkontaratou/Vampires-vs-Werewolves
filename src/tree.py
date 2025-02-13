from .map import *
from .heuristics import *


class Node:
    def __init__(self, state, value=- float('inf'), parent=None):
        self.state: GameMap = state
        self.value = value
        self.parent = parent
        self.children = []

    def addChild(self, child_node):
        self.children.append(child_node)


class Tree:
    def __init__(self):
        self.root = None

    def create_tree(self, map: GameMap, depth):
        self.root = Node(map)

        if not bool(self.root.state.vamps_state) or not bool(self.root.state.wolves_state):
            self.root = evaluate_game_state(self.root.state)
            return
        else:
            find_children(map, self.root)
            self.build_tree(self.root, depth - 1)

    def build_tree(self, parent: Node, depth):
        if depth < 1:
            for child in parent.children:
                child.value = evaluate_game_state(child.state)
            return

        for child in parent.children:
            if not bool(child.state.vamps_state) or not bool(child.state.wolves_state):
                child.value = evaluate_game_state(child.state)
                return
            else:
                child.value = None
                child.state.is_vampire = not child.state.is_vampire

                find_children(child.state, child)
                self.build_tree(child, depth - 1)

    def print_tree(self, node=None, prefix="", depth=0, is_last=True):
        if node is None:
            node = self.root

        if isinstance(node, Node):
            # Define connectors for the tree
            branch = "└── " if is_last else "├── "
            child_prefix = "    " if is_last else "│   "
            
            # Extract state information for printing
            current_pos = node.state.get_current_pos()
            vamp_count = sum(node.state.vamps_state.values())
            wolf_count = sum(node.state.wolves_state.values())
            human_count = sum(node.state.humans_state.values())

            # Print the node information
            print(f"{prefix}{branch}Depth {depth}: Position {current_pos[0] if current_pos else 'N/A'} | "
                f"Vampires: {vamp_count} | Wolves: {wolf_count} | Humans: {human_count} | "
                f"Value: {node.value}")

            # Recursively print children with updated prefix
            child_count = len(node.children)
            for i, child in enumerate(node.children):
                self.print_tree(child, prefix + child_prefix, depth + 1, i == child_count - 1)



def find_children(game_map: GameMap, parent: Node):
    moves = game_map.possible_moves()
    maps = new_maps(game_map, moves)

    for game_map, move in zip(maps, moves):
        leaf_node = Node(game_map)
        leaf_node.parent = parent
        parent.addChild(leaf_node)

    return


def new_maps(game_map: GameMap, moves):
    nodes = []
    for move in moves:
        new_map = game_map.generate_updated_map(move)
        nodes.append(new_map)
    return nodes



