import heapq

class AStarSolver:
    def __init__(self, board, initial_positions, target_color, target_pos, max_depth=30):
        """
        Args:
            board (list): 2D list representing the game board cells. Each cell is a dict with "walls".
            initial_positions (dict): Mapping from robot color to position tuple (row, col).
            target_color (str): The color of the robot that must reach the target.
            target_pos (tuple): The target cell position (row, col).
            max_depth (int): Maximum number of moves (depth) to search.
        """
        self.board = board
        self.initial_positions = initial_positions
        self.target_color = target_color
        self.target_pos = target_pos
        self.max_depth = max_depth

    def a_star_search(self, progress_callback=None):
        """
        Run the A* search to find a sequence of moves that leads the target robot to the target.
        
        Args:
            progress_callback (callable): Optional callback function to report progress
                                        and check for cancellation
        
        Returns:
            list: A list of (color, direction) moves, or None if no solution is found.
        """
        open_set = []
        visited = {}
        start_state = self.initial_positions
        start_key = self._get_state_key(start_state)
        g_cost = 0
        h_cost = self._heuristic(start_state)
        entry = (g_cost + h_cost, 0, start_state, [])
        heapq.heappush(open_set, entry)
        visited[start_key] = 0
        counter = 1
        states_explored = 0

        while open_set:
            # Periodically report progress and check for cancellation
            states_explored = len(visited)
            if progress_callback and counter % 100 == 0:  # Update every 100 expansions
                if not progress_callback(states_explored):
                    # If callback returns False, the search was cancelled
                    return None

            f, _, current_state, moves = heapq.heappop(open_set)
            if len(moves) >= self.max_depth:
                continue
            if self._is_goal(current_state):
                # Report final stats before returning
                if progress_callback:
                    progress_callback(states_explored)
                return moves

            for color in current_state.keys():
                for direction in ["N", "S", "E", "W"]:
                    new_state, moved = self._move_robot(current_state, color, direction)
                    if not moved:
                        continue
                    new_moves = moves + [(color, direction)]
                    new_key = self._get_state_key(new_state)
                    new_g_cost = len(new_moves)
                    # Prune states that have already been reached with a lower cost.
                    if new_key in visited and visited[new_key] <= new_g_cost:
                        continue
                    visited[new_key] = new_g_cost
                    new_h_cost = self._heuristic(new_state)
                    heapq.heappush(open_set, (new_g_cost + new_h_cost, counter, new_state, new_moves))
                    counter += 1
        
        # Report final stats before returning None
        if progress_callback:
            progress_callback(states_explored)
        # If no solution is found within maximum depth, return None.
        return None

    def _is_goal(self, positions):
        """Check if the target robot reached the target position."""
        return positions[self.target_color] == self.target_pos

    def _heuristic(self, positions):
        """
        Use Manhattan distance for the target robot as the heuristic.
        """
        robot_x, robot_y = positions[self.target_color]
        target_x, target_y = self.target_pos
        return abs(robot_x - target_x) + abs(robot_y - target_y)

    def _move_robot(self, positions, color, direction):
        """
        Simulate moving a robot until it hits a wall or another robot.
        
        Args:
            positions (dict): Current positions mapping.
            color (str): The color of the robot to move.
            direction (str): Direction to move: 'N', 'S', 'E', or 'W'.
            
        Returns:
            (dict, bool): New positions dict and a bool flag indicating if the robot moved.
        """
        # Determine movement direction
        dx, dy = 0, 0
        if direction == "N":
            dx = -1
        elif direction == "S":
            dx = 1
        elif direction == "W":
            dy = -1
        elif direction == "E":
            dy = 1

        x, y = positions[color]
        new_x, new_y = x, y

        while True:
            # Check if current cell has a wall blocking movement in the desired direction.
            if direction in self.board[new_x][new_y]["walls"]:
                break
            next_x, next_y = new_x + dx, new_y + dy
            # Check board boundaries.
            if not (0 <= next_x < len(self.board) and 0 <= next_y < len(self.board[0])):
                break
            # Check for an opposite wall in the next cell.
            opposite = {"N": "S", "S": "N", "E": "W", "W": "E"}[direction]
            if opposite in self.board[next_x][next_y]["walls"]:
                break
            # Check for collisions with other robots.
            collision = False
            for other_color, pos in positions.items():
                if other_color != color and pos == (next_x, next_y):
                    collision = True
                    break
            if collision:
                break
            new_x, new_y = next_x, next_y

        moved = (new_x, new_y) != (x, y)
        if moved:
            new_positions = dict(positions)
            new_positions[color] = (new_x, new_y)
            return new_positions, True
        return positions, False

    def _get_state_key(self, positions):
        """
        Return a hashable representation of the state.
        The state is represented as a tuple of sorted (color, pos) pairs.
        """
        return tuple(sorted(positions.items()))