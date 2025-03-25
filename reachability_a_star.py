import heapq
import time

class ReachabilityAStarSolver:
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
        self.board_size = len(board)
        
        # Initialize the reach map for the target position
        self.target_reach_map = self._create_distance_map(self.target_pos)

    def a_star_search(self, progress_callback=None):
        """
        Run the A* search with reachability-based heuristic to find a solution.
        
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
        
        start_time = time.time()
        last_report_time = start_time

        while open_set:
            # Periodically report progress and check for cancellation
            states_explored = len(visited)
            current_time = time.time()
            
            # Report progress every 100 expansions or every 0.5 seconds
            if progress_callback and (counter % 100 == 0 or current_time - last_report_time > 0.5):
                last_report_time = current_time
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
        Use reachability-based heuristic that considers walls and movement constraints.
        """
        robot_pos = positions[self.target_color]
        
        # Use cached distance if available
        if robot_pos in self.target_reach_map:
            return self.target_reach_map[robot_pos]
        
        # Fallback to Manhattan distance if not in the reachability map
        robot_x, robot_y = robot_pos
        target_x, target_y = self.target_pos
        return abs(robot_x - target_x) + abs(robot_y - target_y)

    def _create_distance_map(self, target_pos):
        """
        Creates a map of minimum distances from every cell to the target position,
        taking into account the walls and movement constraints.
        """
        distance_map = {}
        queue = [(target_pos, 0)]  # (position, distance)
        visited = {target_pos}
        
        while queue:
            pos, dist = queue.pop(0)
            distance_map[pos] = dist
            
            # For each direction, find the furthest position the robot can move
            for direction in ["N", "S", "E", "W"]:
                next_pos, moved = self._get_next_position(pos, direction)
                if moved and next_pos not in visited:
                    visited.add(next_pos)
                    queue.append((next_pos, dist + 1))
                    
        return distance_map
    
    def _get_next_position(self, pos, direction):
        """
        Compute the next position when moving in a direction from a position
        without considering other robots (used for heuristic calculation).
        """
        x, y = pos
        dx, dy = 0, 0
        if direction == "N":
            dx = -1
        elif direction == "S":
            dx = 1
        elif direction == "W":
            dy = -1
        elif direction == "E":
            dy = 1
            
        new_x, new_y = x, y
        
        while True:
            # Check if current cell has a wall blocking movement
            if direction in self.board[new_x][new_y]["walls"]:
                break
                
            next_x, next_y = new_x + dx, new_y + dy
            
            # Check board boundaries
            if not (0 <= next_x < self.board_size and 0 <= next_y < self.board_size):
                break
                
            # Check for opposite wall in next cell
            opposite = {"N": "S", "S": "N", "E": "W", "W": "E"}[direction]
            if opposite in self.board[next_x][next_y]["walls"]:
                break
                
            new_x, new_y = next_x, next_y
            
        return (new_x, new_y), (new_x, new_y) != pos

    def _move_robot(self, positions, color, direction):
        """
        Simulate moving a robot until it hits a wall or another robot.
        """
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
            if direction in self.board[new_x][new_y]["walls"]:
                break
            next_x, next_y = new_x + dx, new_y + dy
            if not (0 <= next_x < self.board_size and 0 <= next_y < self.board_size):
                break
            opposite = {"N": "S", "S": "N", "E": "W", "W": "E"}[direction]
            if opposite in self.board[next_x][next_y]["walls"]:
                break
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
        """
        return tuple(sorted(positions.items()))
