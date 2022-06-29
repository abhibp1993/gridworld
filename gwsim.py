from esm import ESM
import pygame
import logging
import sys
import vis_utils
import random


COLOR_GRIDLINES = (175, 175, 175)
TIMER_STEP_MS = 500


class GWSim(ESM):
    MODE_MANUAL = "manual"
    MODE_AUTO = "auto"

    def __init__(self, gw_graph, screen_dim, step_duration=TIMER_STEP_MS, len_history=float("inf")):
        super(GWSim, self).__init__(gw_graph, len_history)
        self.screen_width = screen_dim[0]
        self.screen_height = screen_dim[1]
        self.col_width = self.screen_width // self.graph.dim[1]
        self.row_height = self.screen_height // self.graph.dim[0]
        self.tile_size = (self.col_width // 5, self.row_height // 5)
        self.p2_sprite = None
        self.nature_sprite = None
        self.background_sprite = None
        self.p1_sprite = None
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.mode = GWSim.MODE_MANUAL
        self.step_duration = step_duration

    def initialize(self, state):
        # Initialize state machine
        super(GWSim, self).initialize(state)

        # Initialize positions of sprites
        if self.p1_sprite is not None:
            self.p1_sprite.move(state)
        if self.p2_sprite is not None:
            self.p2_sprite.move(state)
        if self.nature_sprite is not None:
            self.nature_sprite.move(state)
        if self.background_sprite is not None:
            self.background_sprite.move(state)

    def add_p1_sprite(self, sprite):
        self.p1_sprite = sprite

    def add_p2_sprite(self, sprite):
        self.p2_sprite = sprite

    def add_nature_sprite(self, sprite):
        self.nature_sprite = sprite

    def add_background_sprite(self, sprite):
        self.background_sprite = sprite

    def draw_grid(self):
        # Draw grid lines
        for x in range(0, self.screen_width, self.col_width):
            for y in range(0, self.screen_height, self.row_height):
                rect = pygame.Rect(x, y, self.col_width, self.row_height)
                pygame.draw.rect(self.screen, COLOR_GRIDLINES, rect, 1)

    def terminate(self, *args, **kwargs):
        # TODO. Save the play and exit.
        # file = self.generate_file_name()
        # self.save(file)

        # Quit game
        pygame.display.quit()
        pygame.quit()
        sys.exit()

    def grid2world(self, cell):
        """
        Returns the world-coordinates (in pixels) of the center of cell.
        """
        x = (self.graph.dim[0] - cell[0] - 1) * self.row_height + self.row_height // 2
        y = cell[1] * self.col_width + self.col_width // 2
        return x, y

    def world2grid(self, world):
        """
        Returns the cell (row, col) to which the given coordinates belong to.
        """
        return world[0] // self.row_height, world[1] // self.col_width

    def run(self):
        # Initialize pygame
        pygame.init()

        # Alert user about origin.
        print(vis_utils.BColors.OKGREEN, "Origin @ top-left cell. Rows: Top -> Bottom. Cols: Left -> Right",
              vis_utils.BColors.ENDC)

        # Update window caption
        if self.mode == GWSim.MODE_MANUAL:
            pygame.display.set_caption('GWSim (mode: MANUAL)')
            print(vis_utils.BColors.OKGREEN, "Setting mode to MANUAL", vis_utils.BColors.ENDC)
            logging.debug("Setting mode to MANUAL")
        else:
            pygame.display.set_caption('GWSim (mode: AUTO)')
            print(vis_utils.BColors.OKGREEN, "Setting mode to AUTO", vis_utils.BColors.ENDC)
            logging.debug("Setting mode to AUTO")

        # Main loop
        while True:
            # Get all events in queue
            events = pygame.event.get()

            # Handle events
            self.handle_events(events)

            # (mode: AUTO) Step the state machine
            if self.mode == GWSim.MODE_AUTO:
                self.step_forward()

            # Fill the screen with white
            self.screen.fill((255, 255, 255))

            # Draw Gridworld
            self.draw_grid()

            # Update sprite positions based on current state
            self.render_state()

            # Update screen
            pygame.display.flip()

            # Control FPS
            if self.mode == GWSim.MODE_AUTO:
                pygame.time.delay(self.step_duration)

    def step_forward(self):
        if self.step_counter < len(self.state_history) - 1:
            self.step_counter += 1
            logging.debug(f"Step counter points to history. Incremented to {self.step_counter}")
            return

        # TODO. Implement transition.

        # # Validate transition
        # if not self.graph.has_node(next_node):
        #     err_msg = f"Node: {next_node} not in transition system. " \
        #               f"Call tsys.delta({self.curr_node}, {(p1_act, nature_act)}) resulted in {next_node}."
        #     logging.error(err_msg)
        #     raise ValueError(err_msg)
        # 
        # # Apply transition to game
        # self.state_history.append(next_node)
        # self.action_history.append((p1_act, nature_act))
        # self.step_counter += 1
        # logging.debug(f"Step counter advanced to new state. Incremented to {self.step_counter}.")

    def step_backward(self):
        if self.step_counter > 0:
            self.step_counter -= 1
        else:
            print(vis_utils.BColors.WARNING, "Cannot step backwards. Step counter @ 0.", vis_utils.BColors.ENDC)
        print(f"step counter: {self.step_counter}")

    def justify(self):
        # TODO
        #  1. Justify the strategy of players on current state.
        pass

    def toggle_mode(self):
        if self.mode == GWSim.MODE_MANUAL:
            self.mode = GWSim.MODE_AUTO
        else:
            self.mode = GWSim.MODE_MANUAL

    def render_state(self):
        # # Get current state from node
        # curr_state = self.graph.node2state(self.curr_state)

        # Move player1 sprite
        self.p1_sprite.move(self.curr_state)
        self.screen.blit(self.p1_sprite.surf, self.p1_sprite.rect)

        # Move cloud sprite
        if self.nature_sprite is not None:
            self.nature_sprite.move(self.curr_state)
            self.screen.blit(self.nature_sprite.surf, self.nature_sprite.rect)

        # TODO. How to handle collisions?
        # # Check collision state (If colliding, offset them to avoid overlapping)
        # if self.p1_sprite.position == self.nature_sprite.position:
        #     self.p1_sprite.rect.left += self.tile_size[0] // 2
        #     self.p1_sprite.rect.top += self.tile_size[1] // 2
        #     self.nature_sprite.rect.left -= self.tile_size[0] // 2
        #     self.nature_sprite.rect.top -= self.tile_size[1] // 2
        if self.background_sprite is not None:
            for obs in self.background_sprite:
                self.screen.blit(obs.surf, obs.rect)

    def handle_events(self, events):
        # Call event handlers
        for event in events:
            # Did the user click the window close button? If so, stop the loop.
            if event.type == pygame.QUIT:
                logging.debug("[pygame Event] pygame.QUIT")
                self.terminate()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    logging.debug("[pygame Event] pygame.KEYDOWN && pygame.K_ESCAPE")
                    self.terminate()

                elif event.key == pygame.K_RIGHT and self.mode == GWSim.MODE_MANUAL:
                    logging.debug("[pygame Event] pygame.KEYDOWN && pygame.K_RIGHT")
                    self.step_forward()

                elif event.key == pygame.K_LEFT and self.mode == GWSim.MODE_MANUAL:
                    logging.debug("[pygame Event] pygame.KEYDOWN && pygame.K_LEFT")
                    self.step_backward()

                elif event.key == pygame.K_j and self.mode == GWSim.MODE_MANUAL:
                    logging.debug("[pygame Event] pygame.KEYDOWN && pygame.K_j")
                    print("Call justify()")
                    self.justify()

                elif event.key == pygame.K_t:
                    logging.debug("[pygame Event] pygame.KEYDOWN && pygame.K_t")
                    self.toggle_mode()
                    if self.mode == GWSim.MODE_MANUAL:
                        pygame.display.set_caption('GWSim (mode: AUTO)')
                        pygame.event.pump()
                        logging.debug(f"Mode changed from {GWSim.MODE_MANUAL} -> {GWSim.MODE_AUTO}.")
                    else:
                        pygame.display.set_caption('GWSim (mode: MANUAL)')
                        pygame.event.pump()
                        logging.debug(f"Mode changed from {GWSim.MODE_AUTO} -> {GWSim.MODE_MANUAL}.")