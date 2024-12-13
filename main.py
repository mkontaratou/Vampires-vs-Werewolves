from argparse import ArgumentParser
from src.client import ClientSocket
from src.map import GameMap
from src.tree import Tree
from src.alphabeta import AlphaBeta
import traceback

class ServerInterface:
    def __init__(self, ip, port, name):
        self.ip = ip
        self.port = port
        self.name = name

        # Connection with server
        self.client = ClientSocket(self.ip, self.port)
        self.client.send_nme(self.name)

        for _ in range(0, 4):
            key, value = self.client.get_message()
            self._parse_message(key, value)


    def _parse_message(self, key, value, isUpdate=False):
        if key == 'set':
            self.board_height, self.board_width = value
        elif key == 'hme':
            self.init_pos = value
        elif key == 'map':
            self.map = value
        elif key == 'upd':
            self.update = value
            if isUpdate:
                isUpdate.update_map(value)
        elif key == 'hum':
            self.homes = value
        else:
            raise ValueError('Unexpected command from server!')

    def send_move(self, nb_players, current_pos, target_pos):
        self.client.send_mov(1, [current_pos, nb_players, target_pos])

    def update_board(self, board):
        key, value = self.client.get_message()
        self._parse_message(key, value, board)
        return key


DEPTH = 3  # should always be odd so that we are maximizing us in the leaves

# Reading of data GameMap
# Sending data to server Player
def play_game(server):
    game_map: GameMap = GameMap(server.board_height, server.board_width, server.map, server.init_pos)

    while True:
        # Check if the upd is empty to make move
        update_key = server.update_board(game_map)

        if update_key == 'upd':
            game_map.display_state()

            data_tree = Tree()
            data_tree.create_tree(game_map, depth=DEPTH)
            data_tree.print_tree()

            alphabeta = AlphaBeta(data_tree)
            best_move = alphabeta.alpha_beta_search(data_tree.root)

            current_pos, current_nb = game_map.get_biggest_position()
            target_pos, _ = best_move.state.get_enemy_biggest_position()
            
            if type(target_pos) is int:
                target_pos, _ = best_move.state.get_biggest_position()

            server.send_move([current_nb], list(current_pos), list(target_pos))

if __name__ == '__main__':
    parser = ArgumentParser()

    parser.add_argument(dest='ip', default='localhost', type=str, help='IP address the connection should be made to.')
    parser.add_argument(dest='port', default='5555', type=int, help='Chosen port for the connection.')
    parser.add_argument(dest='name', type=str, help='Name of IA')

    args = parser.parse_args()

    try:
        server = ServerInterface(args.ip,args.port,args.name)

        play_game(server)
    except Exception as e:
        print(f"{e.__class__} occurred: {str(e)}")
        # traceback.print_exc()
        print("Game over")