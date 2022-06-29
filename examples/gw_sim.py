import argparse
import logging
import os
import pprint
import pygame

from gridworld import graphify
from gwsim import GWSim
from examples.stoch_gw_qualitative import StochasticGridworld


class Player1(pygame.sprite.Sprite):
    def __init__(self, parent, position):
        super(Player1, self).__init__()
        self.parent = parent
        self.surf = pygame.Surface(parent.tile_size)
        self.surf.fill((0, 0, 255))
        self.position = position  # cell in gridworld
        self.rect = self.surf.get_rect()
        # self.move()

    def move(self, state):
        """
        State structure: (p1.row, p1.col)
        """
        self.position = tuple(state)
        x, y = self.parent.grid2world(self.position)
        self.rect.top = x - self.parent.tile_size[0] // 2
        self.rect.left = y - self.parent.tile_size[1] // 2


class Cloud(pygame.sprite.Sprite):
    def __init__(self, parent, position):
        super(Cloud, self).__init__()
        self.parent = parent
        self.surf = pygame.Surface(parent.tile_size)
        self.surf.fill((0, 255, 255))
        self.position = position  # cell in gridworld
        self.rect = self.surf.get_rect()
        # self.move()

    def move(self, state):
        self.position = (state[3], self.position[1])
        x, y = self.parent.grid2world(self.position)
        self.rect.top = x - self.parent.tile_size[0] // 2
        self.rect.left = y - self.parent.tile_size[1] // 2


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, parent, position):
        super(Obstacle, self).__init__()
        self.parent = parent
        self.surf = pygame.Surface((parent.col_width, parent.row_height))
        self.surf.fill((0, 0, 0))
        self.position = position  # cell in gridworld
        self.rect = self.surf.get_rect()
        self.rect.top = self.position[0] * self.parent.row_height
        self.rect.left = self.position[1] * self.parent.col_width

    def move(self):
        pass


def setup_logging(args):
    try:
        #  Get log file name
        if args.log_file is not None:
            log_file = args.log_file
        else:
            # Hint: https://www.programiz.com/python-programming/examples/file-name-from-file-path
            conf_file_name = os.path.splitext(os.path.basename(args.tsys.name))[0]
            log_file = os.path.join("logs", f"{conf_file_name}_sim.log")
    except:
        log_file = "gw_sim.log"     # PATCH. Remove later.

    # Remove the log file, if exists.
    if os.path.isfile(log_file):
        print("removing log file:", os.path.abspath(log_file))
        os.remove(os.path.abspath(log_file))

    # Determine logging level
    if args.log_level == "debug":
        log_level = logging.DEBUG
    elif args.log_level == "info":
        log_level = logging.INFO
    elif args.log_level == "warn":
        log_level = logging.WARN
    elif args.log_level == "error":
        log_level = logging.ERROR
    else:
        log_level = logging.CRITICAL

    # Configure logger
    logging.basicConfig(
        level=log_level,
        filename=log_file,
        format='[%(levelname)s] [%(filename)s:%(funcName)s:%(lineno)d] %(message)s'
    )


def main(args):
    # Set up logger
    setup_logging(args)

    # Set up pretty printing for console output
    pp = pprint.PrettyPrinter(indent=2)

    # Define MDP gridworld model
    mdp = StochasticGridworld(dim=(5, 5))
    mdp_graph = graphify(mdp)
    print(mdp)
    print(mdp_graph)

    # # Log, print loaded configuration
    # logging.info(f"Loaded {mdp.__class__.__name__} object with configuration: \n{pp.pformat(mdp.gw_conf)}\n")
    # print()
    # print("[INFO] Gridworld configuration:")
    # pp.pprint(mdp.gw_conf)
    # print()

    # Create GWSim instance
    sim = GWSim(gw_graph=mdp_graph, screen_dim=[800, 600])
    logging.info(f"Created GWSim instance with "
                 f"\n\t- screen dimensions: {(sim.screen_width, sim.screen_height)}"
                 f"\n\t- step_duration: {sim.step_duration}"
                 f"\n\t- len_history: {sim.len_history}"
                 )
    print(f"[INFO] GWSim instance created.")

    # Create player sprite
    p1 = Player1(parent=sim, position=(0, 0))
    # cloud = Cloud(parent=sim, position=(2, 3))
    # obs1 = Obstacle(parent=sim, position=(2, 2))

    sim.add_p1_sprite(sprite=p1)
    # sim.add_nature_sprite(sprite=cloud)
    # sim.add_sprites(obs=[obs1])

    # Run simulation
    init_state = (1, 2)
    sim.initialize(init_state)
    logging.info(f"Initialized GWSim with node {mdp_graph.state2node(init_state)}:{init_state}.")
    print(f"[INFO] Initialized GWSim with node {mdp_graph.state2node(init_state)}:{init_state}.")

    # Start simulation
    print("[INFO] Starting simulation")
    sim.run()


if __name__ == '__main__':
    # Command line argument parser
    parser = argparse.ArgumentParser()
    # parser.add_argument('--tsys',
    #                     type=argparse.FileType('rb'),
    #                     required=True,
    #                     help="Path to transition system file (.tsys)."
    #                     )
    parser.add_argument('--log_level',
                        type=str,
                        required=False,
                        default="info",
                        help="Level of python logging module (debug, info [default], warn, error, critical)."
                        )
    parser.add_argument('--log_file',
                        type=argparse.FileType('r'),
                        required=False,
                        default=None,
                        help="Path where log file should be stored [Default: 'logs/<name of gwconf file>_2tsys.log']."
                        )

    args_ = parser.parse_args()

    # Run gridworld construction
    main(args_)
