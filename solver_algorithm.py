import heapq
from collections import deque
import tkinter as tk
from tkinter import messagebox, simpledialog
from ui import RicochetRobotsGame

class RicochetRobotsSolver:
    def __init__(self, game):
        """
        Initialize the solver with the game instance.
        
        Args:
            game: The RicochetRobotsGame instance
        """
        self.game = game
        self.solution = None
        self.solution_index = 0
        
    def prepare_board_for_solver(self):
        """Convert the game board to the format required by the solver."""
        # Create a 2D grid where 1 represents walls
        board = [[0 for _ in range(self.game.GRID_SIZE)] for _ in range(self.game.GRID_SIZE)]
        
        # Mark walls in the board
        for x in range(self.game.GRID_SIZE):
            for y in range(self.game.GRID_SIZE):
                cell = self.game.board[x][y]
                # If there are walls in multiple directions, mark as obstacle
                if len(cell["walls"]) > 0:
                    board[x][y] = 1
        
        return board
    
    def get_robot_positions(self):
        """Get current robot positions in the format required by the solver."""
        robots_dict = {}
        for color, robot in self.game.robots.items():
            robots_dict[color] = robot["pos"]
        return robots_dict
    
    def solve(self):
        """Run the A* search algorithm to find the solution."""
        # Prepare data for solver
        board = self.prepare_board_for_solver()
        robots = self.get_robot_positions()
        goal_robot = self.game.current_target["color"]
        goal_position = self.game.current_target["pos"]
        
        # Create solver instance
        solver = AStarSolver(board, robots, goal_robot, goal_position)
        
        # Find solution
        self.solution = solver.a_star_search()
        self.solution_index = 0
        
        if self.solution:
            messagebox.showinfo("Solution Found", 
                              f"Solution found in {len(self.solution)} moves.\n"
                              "Click 'Show Hint' to see the next move.")
            return True
        else:
            messagebox.showinfo("No Solution", "No solution could be found.")
            return False
    
    def get_next_move(self):
        """Get the next move in the solution sequence."""
        if not self.solution or self.solution_index >= len(self.solution):
            return None
            
        move = self.solution[self.solution_index]
        self.solution_index += 1
        return move
    
    def show_hint(self):
        """Show the next move as a hint."""
        if not self.solution:
            messagebox.showinfo("No Solution", "No solution available. Click 'Solve' first.")
            return
            
        if self.solution_index >= len(self.solution):
            messagebox.showinfo("End of Solution", "No more moves in the solution.")
            return
            
        move = self.get_next_move()
        robot_color, new_position = move
        
        # Highlight the robot to move
        for color in self.game.robots:
            self.game.robots[color]["selected"] = (color == robot_color)
        
        # Show hint message
        current_pos = self.game.robots[robot_color]["pos"]
        hint_direction = self._get_direction(current_pos, new_position)
        
        messagebox.showinfo("Hint", 
                          f"Move the {robot_color} robot {hint_direction}.\n"
                          f"({self.solution_index}/{len(self.solution)} moves)")
        
        self.game.draw_board()
    
    def _get_direction(self, current_pos, new_pos):
        """Determine the direction to move from current position to new position."""
        cx, cy = current_pos
        nx, ny = new_pos
        
        if nx < cx:
            return "Up"
        elif nx > cx:
            return "Down"
        elif ny < cy:
            return "Left"
        elif ny > cy:
            return "Right"
        return "Unknown"
    
    def auto_solve(self):
        """Automatically execute all moves in the solution."""
        if not self.solution:
            messagebox.showinfo("No Solution", "No solution available. Click 'Solve' first.")
            return
            
        # Reset solution index to start from beginning
        self.solution_index = 0
        
        # Reset game to initial positions
        self.game.reset_positions()
        
        # Execute moves with delay
        self._execute_next_move()
    
    def _execute_next_move(self):
        """Execute the next move with a delay between moves."""
        if self.solution_index >= len(self.solution):
            return
            
        move = self.get_next_move()
        robot_color, new_position = move
        
        # Select the robot
        for color in self.game.robots:
            self.game.robots[color]["selected"] = (color == robot_color)
        
        # Determine direction
        current_pos = self.game.robots[robot_color]["pos"]
        direction = self._get_move_direction(current_pos, new_position)
        
        # Move the robot
        if direction:
            self.game.move_robot(robot_color, direction)
        
        # Schedule next move
        if self.solution_index < len(self.solution):
            self.game.root.after(500, self._execute_next_move)
    
    def _get_move_direction(self, current_pos, new_pos):
        """Convert positions to game direction (N, S, E, W)."""
        cx, cy = current_pos
        nx, ny = new_pos
        
        # Determine primary direction
        if nx < cx:
            return "N"  # Up
        elif nx > cx:
            return "S"  # Down
        elif ny < cy:
            return "W"  # Left
        elif ny > cy:
            return "E"  # Right
        return None


class AStarSolver:
    def __init__(self, board, robots, goal_robot, goal_position):
        """
        Initialize the A* solver.
        
        Args:
            board: 2D list representing walls (1) and open spaces (0)
            robots: Dictionary with robot colors as keys and positions as values
            goal_robot: The robot color that needs to reach the goal
            goal_position: The (x, y) coordinate of the goal
        """
        self.board = board
        self.robots = robots  # {'red': (x, y), 'green': (x, y), ...}
        self.goal_robot = goal_robot
        self.goal_position = goal_position
        self.height = len(board)
        self.width = len(board[0]) if self.height > 0 else 0
        
        # Precompute shortest paths to goal
        self.goal_distances = self.precompute_goal_distances()

    def precompute_goal_distances(self):
        """Use BFS to precompute distances from all board positions to the goal."""
        distances = [[float('inf')] * self.width for _ in range(self.height)]
        queue = deque([self.goal_position])
        distances[self.goal_position[0]][self.goal_position[1]] = 0

        directions = [(0,1), (0,-1), (1,0), (-1,0)]
        
        while queue:
            x, y = queue.popleft()
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.height and 0 <= ny < self.width and self.board[nx][ny] == 0:
                    if distances[nx][ny] == float('inf'):
                        distances[nx][ny] = distances[x][y] + 1
                        queue.append((nx, ny))

        return distances

    def heuristic(self, state):
        """Compute heuristic h(n) as a combination of flood fill distance and bounce count."""
        robots, _ = state
        target_x, target_y = robots[self.goal_robot]
        
        # If goal is reached, heuristic is 0
        if (target_x, target_y) == self.goal_position:
            return 0
            
        # Distance from precomputed BFS
        base_h = self.goal_distances[target_x][target_y]
        
        # Estimate number of required bounces
        bounces = self.estimate_bounces(robots[self.goal_robot])
        
        # Count blocking robots
        blocking_penalty = sum(1 for robot, pos in robots.items() 
                              if robot != self.goal_robot and self.is_blocking(pos))
        
        return base_h + 2 * bounces + blocking_penalty

    def estimate_bounces(self, position):
        """Estimate the number of bounces required to reach the goal."""
        x, y = position
        goal_x, goal_y = self.goal_position
        
        # Count necessary direction changes
        bounces = 0
        if x != goal_x:
            bounces += 1
        if y != goal_y:
            bounces += 1
            
        return bounces

    def is_blocking(self, robot_position):
        """Determine if a robot is blocking the direct path to the goal."""
        rx, ry = robot_position
        gx, gy = self.goal_position
        
        if rx == gx or ry == gy:  # Only relevant if it's aligned with the goal
            return True
        return False

    def get_valid_moves(self, robots):
        """Generate all possible moves from the current state."""
        moves = []
        for robot, (x, y) in robots.items():
            for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]:
                nx, ny = x, y
                while self.is_valid_move(nx + dx, ny + dy, robots):
                    nx += dx
                    ny += dy
                if (nx, ny) != (x, y):
                    new_robots = robots.copy()
                    new_robots[robot] = (nx, ny)
                    moves.append((new_robots, (robot, (nx, ny))))  # New state + move taken
        return moves

    def is_valid_move(self, x, y, robots):
        """Check if the robot can move to (x, y) without hitting walls or another robot."""
        if not (0 <= x < self.height and 0 <= y < self.width):
            return False
        if self.board[x][y] == 1:  # Wall
            return False
        if (x, y) in robots.values():  # Another robot
            return False
        return True

    def a_star_search(self):
        """A* search algorithm to find the optimal solution."""
        initial_state = (self.robots, [])
        priority_queue = [(self.heuristic(initial_state), 0, initial_state)]  # (f(n), g(n), state)
        visited = set()
        
        max_iterations = 50000  # Limit iterations to prevent too long searches
        iterations = 0

        while priority_queue and iterations < max_iterations:
            iterations += 1
            _, g, (robots, path) = heapq.heappop(priority_queue)
            
            if robots[self.goal_robot] == self.goal_position:
                return path  # Solution found!
            
            state_key = tuple(sorted(robots.items()))
            if state_key in visited:
                continue
            visited.add(state_key)
            
            for new_state, move in self.get_valid_moves(robots):
                new_path = path + [move]
                f = g + 1 + self.heuristic((new_state, new_path))
                heapq.heappush(priority_queue, (f, g + 1, (new_state, new_path)))
        
        return None  # No solution found or exceeded max iterations


# Class to extend the RicochetRobotsGame with solver functionality
def add_solver_to_game(game_class):
    """Add solver functionality to the RicochetRobotsGame class."""
    
    # Store original __init__ method
    original_init = game_class.__init__
    
    def new_init(self, root):
        """Extended initialization with solver integration."""
        # Call original __init__
        original_init(self, root)
        
        # Add solver
        self.solver = RicochetRobotsSolver(self)
        
        # Add solver UI elements
        self._add_solver_ui()
    
    def _add_solver_ui(self):
        """Add UI elements for the solver."""
        # Add solver section to right frame
        self.solver_frame = tk.Frame(self.right_frame, relief=tk.GROOVE, bd=2)
        self.solver_frame.pack(fill=tk.X, pady=10)
        
        self.solver_title = tk.Label(self.solver_frame, text="Solver", font=("Arial", 12, "bold"))
        self.solver_title.pack(pady=(5, 0))
        
        # Solver buttons
        self.solve_btn = tk.Button(self.solver_frame, text="Find Solution", 
                                 command=self.solver.solve,
                                 font=("Arial", 11), bg="#9C27B0", fg="white", height=1)
        self.solve_btn.pack(fill=tk.X, pady=5, padx=10)
        
        self.hint_btn = tk.Button(self.solver_frame, text="Show Hint", 
                                command=self.solver.show_hint,
                                font=("Arial", 11), bg="#673AB7", fg="white", height=1)
        self.hint_btn.pack(fill=tk.X, pady=5, padx=10)
        
        self.auto_solve_btn = tk.Button(self.solver_frame, text="Auto Solve", 
                                      command=self.solver.auto_solve,
                                      font=("Arial", 11), bg="#3F51B5", fg="white", height=1)
        self.auto_solve_btn.pack(fill=tk.X, pady=5, padx=10)
    
    # Replace __init__ with new implementation
    game_class.__init__ = new_init
    # Add solver UI method
    game_class._add_solver_ui = _add_solver_ui
    
    return game_class


# Modified main function to use the solver-enhanced game
def main():
    root = tk.Tk()
    
    # Enhance game class with solver
    EnhancedGame = add_solver_to_game(RicochetRobotsGame)
    
    # Create game instance
    game = EnhancedGame(root)
    
    root.mainloop()


if __name__ == "__main__":
    main()
    