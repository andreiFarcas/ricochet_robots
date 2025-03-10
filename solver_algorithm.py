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
        # Create a 2D grid where 0 represents open space, 1 represents walls
        board = [[0 for _ in range(self.game.GRID_SIZE)] for _ in range(self.game.GRID_SIZE)]
        
        # Add borders as walls
        for x in range(self.game.GRID_SIZE):
            board[0][x] = 1  # Top border
            board[self.game.GRID_SIZE-1][x] = 1  # Bottom border
            board[x][0] = 1  # Left border
            board[x][self.game.GRID_SIZE-1] = 1  # Right border
        
        # Add internal walls by checking each cell's wall property
        for x in range(self.game.GRID_SIZE):
            for y in range(self.game.GRID_SIZE):
                cell = self.game.board[x][y]
                
                # For each direction, check if there's a wall and update the appropriate cell
                if "N" in cell["walls"] and x > 0:
                    # Wall to the north means the cell to the north is blocked from this cell
                    nx, ny = x-1, y
                    if 0 <= nx < self.game.GRID_SIZE and 0 <= ny < self.game.GRID_SIZE:
                        board[nx][ny] = 1
                        
                if "S" in cell["walls"] and x < self.game.GRID_SIZE-1:
                    # Wall to the south means the cell to the south is blocked from this cell
                    nx, ny = x+1, y
                    if 0 <= nx < self.game.GRID_SIZE and 0 <= ny < self.game.GRID_SIZE:
                        board[nx][ny] = 1
                        
                if "W" in cell["walls"] and y > 0:
                    # Wall to the west means the cell to the west is blocked from this cell
                    nx, ny = x, y-1
                    if 0 <= nx < self.game.GRID_SIZE and 0 <= ny < self.game.GRID_SIZE:
                        board[nx][ny] = 1
                        
                if "E" in cell["walls"] and y < self.game.GRID_SIZE-1:
                    # Wall to the east means the cell to the east is blocked from this cell
                    nx, ny = x, y+1
                    if 0 <= nx < self.game.GRID_SIZE and 0 <= ny < self.game.GRID_SIZE:
                        board[nx][ny] = 1
        
        # Debug output
        print("Solver Board:")
        for row in board:
            print(''.join('#' if cell == 1 else '.' for cell in row))
            
        return board
    
    def get_robot_positions(self):
        """Get current robot positions in the format required by the solver."""
        robots_dict = {}
        for color, robot in self.game.robots.items():
            robots_dict[color] = (robot["pos"][0], robot["pos"][1])  # Ensure positions are tuples
        return robots_dict
    
    def solve(self):
        """Run the A* search algorithm to find the solution."""
        # Prepare data for solver
        board = self.prepare_board_for_solver()
        robots = self.get_robot_positions()
        goal_robot = self.game.current_target["color"]
        goal_position = (self.game.current_target["pos"][0], self.game.current_target["pos"][1])  # Ensure it's a tuple
        
        print(f"Solving for {goal_robot} robot to reach {goal_position}")
        print(f"Initial robot positions: {robots}")
        
        # Create solver instance
        solver = AStarSolver(board, robots, goal_robot, goal_position)
        
        # Find solution
        self.solution = solver.a_star_search()
        self.solution_index = 0
        
        if self.solution:
            print(f"Solution found with {len(self.solution)} moves")
            messagebox.showinfo("Solution Found", 
                              f"Solution found in {len(self.solution)} moves.\n"
                              "Click 'Show Hint' to see the next move.")
            return True
        else:
            print("No solution found")
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
            messagebox.showinfo("Solution Complete", "All moves have been executed.")
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
            self.game.draw_board()  # Ensure board is updated
        
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


class PriorityEntry:
    """Helper class for priority queue that allows comparing entries with same priority"""
    def __init__(self, priority, count, item):
        self.priority = priority
        self.count = count
        self.item = item
        
    def __lt__(self, other):
        # First compare by priority, then by count
        if self.priority == other.priority:
            return self.count < other.count
        return self.priority < other.priority


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
        
        # For debugging
        self._print_board()
        
        # Precompute shortest paths to goal
        self.goal_distances = self.precompute_goal_distances()

    def _print_board(self):
        """Debug function to print the board state."""
        print("Board state:")
        for row in self.board:
            print(''.join('#' if cell == 1 else '.' for cell in row))
        print(f"Robots: {self.robots}")
        print(f"Goal robot: {self.goal_robot} to reach {self.goal_position}")

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

        # Debug output
        print("Distance map to goal:")
        for row in distances:
            print(' '.join(str(cell) if cell != float('inf') else '∞' for cell in row))
                
        return distances

    def get_state_key(self, robots):
        """Create a hashable key for the robot positions."""
        return tuple(sorted((k, robots[k][0], robots[k][1]) for k in robots))

    def heuristic(self, robots):
        """Compute heuristic h(n) for A* search."""
        target_x, target_y = robots[self.goal_robot]
        goal_x, goal_y = self.goal_position
        
        # If goal is reached, heuristic is 0
        if (target_x, target_y) == self.goal_position:
            return 0
            
        # Manhattan distance as a fallback
        manhattan_distance = abs(target_x - goal_x) + abs(target_y - goal_y)
        
        # BFS distance from precomputed matrix (more accurate)
        bfs_distance = self.goal_distances[target_x][target_y]
        
        if bfs_distance != float('inf'):
            return bfs_distance
        
        # If no path found by BFS, use Manhattan distance
        return manhattan_distance

    def get_valid_moves(self, robots):
        """Generate all possible moves from the current state."""
        moves = []
        max_moves = 30  # Safety limit to prevent infinite loops
        
        for robot, (x, y) in robots.items():
            # Try moving in each of the four directions
            for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]:
                nx, ny = x, y
                move_count = 0
                
                # Move robot until it hits something or reaches the limit
                while self.is_valid_move(nx + dx, ny + dy, robots) and move_count < max_moves:
                    nx += dx
                    ny += dy
                    move_count += 1
                
                # Only add move if robot actually moved
                if (nx, ny) != (x, y):
                    new_robots = robots.copy()
                    new_robots[robot] = (nx, ny)
                    moves.append((new_robots, (robot, (nx, ny))))  # New state + move taken
        
        return moves

    def is_valid_move(self, x, y, robots):
        """Check if a position is valid for a robot to occupy."""
        # Check if position is within board bounds
        if not (0 <= x < self.height and 0 <= y < self.width):
            return False
            
        # Check if position has a wall
        if self.board[x][y] == 1:
            return False
            
        # Check if position is occupied by another robot
        if (x, y) in robots.values():
            return False
            
        return True

    def a_star_search(self):
        """A* search algorithm to find the optimal solution."""
        # Use a counter to break ties in priority queue
        counter = 0
        
        # Initial state
        initial_robots = self.robots.copy()
        initial_path = []
        
        # Use a set to track visited states
        visited = set()
        visited_key = self.get_state_key(initial_robots)
        visited.add(visited_key)
        
        # Priority queue for A* using the PriorityEntry helper class
        priority_queue = []
        initial_f_score = self.heuristic(initial_robots)
        heapq.heappush(priority_queue, PriorityEntry(initial_f_score, counter, (0, initial_robots, initial_path)))
        counter += 1
        
        # Print initial state information
        print(f"Starting search with initial robots: {initial_robots}")
        print(f"Goal: {self.goal_robot} robot to position {self.goal_position}")
        print(f"Initial heuristic value: {initial_f_score}")
        
        max_iterations = 500000  # Increase from 50,000 to 500,000
        iterations = 0
        nodes_expanded = 0
        
        while priority_queue and iterations < max_iterations:
            iterations += 1
            
            # Get state with lowest f_score
            entry = heapq.heappop(priority_queue)
            g_score, current_robots, path = entry.item
            
            # Check if goal reached
            if current_robots[self.goal_robot] == self.goal_position:
                print(f"Solution found after {iterations} iterations and {nodes_expanded} nodes expanded")
                print(f"Solution has {len(path)} moves")
                return path
            
            # Generate all possible moves from current state
            nodes_expanded += 1
            for new_robots, move in self.get_valid_moves(current_robots):
                # Check if we've seen this configuration before
                new_key = self.get_state_key(new_robots)
                if new_key in visited:
                    continue
                
                # Mark as visited
                visited.add(new_key)
                
                # Create new path with this move
                new_path = path + [move]
                
                # Calculate scores
                new_g_score = g_score + 1
                h_score = self.heuristic(new_robots)
                f_score = new_g_score + h_score
                
                # Add to priority queue
                heapq.heappush(priority_queue, PriorityEntry(f_score, counter, (new_g_score, new_robots, new_path)))
                counter += 1
            
            if iterations % 5000 == 0:
                print(f"Searched {iterations} states, expanded {nodes_expanded} nodes, queue size: {len(priority_queue)}")
                if priority_queue:
                    best_entry = min(priority_queue, key=lambda x: x.priority)
                    print(f"Current best f_score: {best_entry.priority}")
                    print(f"Current path length: {len(best_entry.item[2])}")
                    print(f"Goal robot position: {current_robots[self.goal_robot]}")
                    print(f"Goal position: {self.goal_position}")
        
        if iterations >= max_iterations:
            print(f"Exceeded iteration limit: {max_iterations}")
        else:
            print("Priority queue empty, no solution exists")
            
        return None  # No solution found


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
        
        # Add debugging output
        print("Game initialized with solver")
        print(f"Target: {self.current_target}")
        for color, robot in self.robots.items():
            print(f"{color} robot at {robot['pos']}")
    
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