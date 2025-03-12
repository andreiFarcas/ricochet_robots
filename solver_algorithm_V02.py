import tkinter as tk
from tkinter import messagebox, simpledialog
import random
import time
import queue

class RicochetRobotsGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Ricochet Robots")
        self.root.geometry("900x720")
        self.root.resizable(True, True)
        
        # Game constants
        self.GRID_SIZE = 16
        self.CELL_SIZE = 40
        self.ROBOT_RADIUS = 15
        self.WALL_WIDTH = 4
        
        # Colors
        self.COLORS = {
            "background": "#E0E0E0",
            "grid": "#CCCCCC",
            "wall": "#333333",
            "target": "#FFD700",
            "robots": {
                "red": "#FF0000",
                "green": "#00CC00",
                "blue": "#0000FF",
                "yellow": "#FFCC00"
            }
        }
        
        # Game state
        self.board = self._create_board()
        self.robots = {
            "red": {"pos": (0, 0), "selected": False},
            "green": {"pos": (0, 0), "selected": False},
            "blue": {"pos": (0, 0), "selected": False},
            "yellow": {"pos": (0, 0), "selected": False}
        }
        self.current_target = {"color": "red", "pos": (0, 0)}
        self.moves_count = 0
        self.best_solution = float('inf')
        self.timer_running = False
        self.start_time = 0
        self.elapsed_time = 0
        self.initial_positions = {}
        
        # Solver state
        self.solution_moves = []
        self.is_showing_solution = False
        self.solution_step_index = 0
        
        # Create main layout frames
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.left_frame = tk.Frame(self.main_frame)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.right_frame = tk.Frame(self.main_frame, width=180)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        self.right_frame.pack_propagate(False)  # Prevent frame from shrinking
        
        # Game board canvas
        self.canvas_frame = tk.Frame(self.left_frame)
        self.canvas_frame.pack(pady=10)
        
        self.canvas = tk.Canvas(self.canvas_frame, width=self.GRID_SIZE*self.CELL_SIZE, 
                               height=self.GRID_SIZE*self.CELL_SIZE, bg=self.COLORS["background"])
        self.canvas.pack()
        
        # Info panel below canvas
        self.info_frame = tk.Frame(self.left_frame)
        self.info_frame.pack(fill=tk.X, pady=5)
        
        self.moves_label = tk.Label(self.info_frame, text="Moves: 0", font=("Arial", 12))
        self.moves_label.pack(side=tk.LEFT, padx=20)
        
        self.target_label = tk.Label(self.info_frame, text="Target: Red", font=("Arial", 12))
        self.target_label.pack(side=tk.LEFT, padx=20)
        
        self.best_label = tk.Label(self.info_frame, text="Best: --", font=("Arial", 12))
        self.best_label.pack(side=tk.LEFT, padx=20)
        
        # Right sidebar with controls and timer
        self.sidebar_title = tk.Label(self.right_frame, text="Game Controls", font=("Arial", 14, "bold"))
        self.sidebar_title.pack(pady=(0, 10))
        
        # Timer display with larger font
        self.timer_frame = tk.Frame(self.right_frame, relief=tk.GROOVE, bd=2)
        self.timer_frame.pack(fill=tk.X, pady=10)
        
        self.timer_title = tk.Label(self.timer_frame, text="Time", font=("Arial", 12))
        self.timer_title.pack(pady=(5, 0))
        
        self.timer_label = tk.Label(self.timer_frame, text="00:00", font=("Arial", 20, "bold"))
        self.timer_label.pack(pady=(0, 5))
        
        # Game controls with larger buttons
        self.control_frame = tk.Frame(self.right_frame)
        self.control_frame.pack(fill=tk.X, pady=10)
        
        self.new_game_btn = tk.Button(self.control_frame, text="New Game", command=self.new_game,
                                     font=("Arial", 12), bg="#4CAF50", fg="white", height=2)
        self.new_game_btn.pack(fill=tk.X, pady=(0, 5))
        
        self.reset_pos_btn = tk.Button(self.control_frame, text="Reset Positions", command=self.reset_positions,
                                     font=("Arial", 12), bg="#2196F3", fg="white", height=2)
        self.reset_pos_btn.pack(fill=tk.X, pady=5)
        
        self.reset_game_btn = tk.Button(self.control_frame, text="Reset Game", command=self.reset_game,
                                     font=("Arial", 12), bg="#FF9800", fg="white", height=2)
        self.reset_game_btn.pack(fill=tk.X, pady=5)
        
        # Add the Solve button
        self.solve_btn = tk.Button(self.control_frame, text="Solve", command=self.solve_game,
                                  font=("Arial", 12), bg="#9C27B0", fg="white", height=2)
        self.solve_btn.pack(fill=tk.X, pady=5)
        
        self.give_up_btn = tk.Button(self.control_frame, text="Give Up", command=self.give_up,
                                     font=("Arial", 12), bg="#F44336", fg="white", height=2)
        self.give_up_btn.pack(fill=tk.X, pady=5)
        
        # Instructions
        self.instructions_frame = tk.Frame(self.right_frame, relief=tk.GROOVE, bd=2)
        self.instructions_frame.pack(fill=tk.X, pady=10)
        
        self.instructions_title = tk.Label(self.instructions_frame, text="How to Play", font=("Arial", 12, "bold"))
        self.instructions_title.pack(pady=(5, 0))
        
        instructions_text = (
            "1. Click a robot to select\n"
            "2. Use arrow keys to move\n"
            "3. Get the matching robot\n   to the target\n"
            "4. Robots move until they\n   hit a wall or robot\n"
            "5. Click 'Solve' to see\n   the solution"
        )
        self.instructions_label = tk.Label(self.instructions_frame, text=instructions_text, 
                                          font=("Arial", 10), justify=tk.LEFT)
        self.instructions_label.pack(pady=5, padx=0)
        
        # Bind events
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.root.bind("<KeyPress>", self.on_key_press)
        
        # Initialize game
        self.new_game()
    
    def _create_board(self):
        # Create an empty board
        board = [[{"walls": set()} for _ in range(self.GRID_SIZE)] for _ in range(self.GRID_SIZE)]
        
        # Add outer walls
        for i in range(self.GRID_SIZE):
            board[0][i]["walls"].add("N")
            board[self.GRID_SIZE-1][i]["walls"].add("S")
            board[i][0]["walls"].add("W")
            board[i][self.GRID_SIZE-1]["walls"].add("E")
        
        # Add central square walls
        for i in range(7, 9):
            for j in range(7, 9):
                if i == 7:
                    board[i][j]["walls"].add("N")
                if i == 8:
                    board[i][j]["walls"].add("S")
                if j == 7:
                    board[i][j]["walls"].add("W")
                if j == 8:
                    board[i][j]["walls"].add("E")
        
        # Add some random internal walls (about 40 walls)
        wall_count = 0
        while wall_count < 40:
            x = random.randint(0, self.GRID_SIZE-2)
            y = random.randint(0, self.GRID_SIZE-2)
            
            # Decide between horizontal or vertical wall
            if random.choice([True, False]):
                # Horizontal wall between (x,y) and (x,y+1)
                if "S" not in board[x][y]["walls"] and "N" not in board[x][y+1]["walls"]:
                    board[x][y]["walls"].add("S")
                    board[x][y+1]["walls"].add("N")
                    wall_count += 1
            else:
                # Vertical wall between (x,y) and (x+1,y)
                if "E" not in board[x][y]["walls"] and "W" not in board[x+1][y]["walls"]:
                    board[x][y]["walls"].add("E")
                    board[x+1][y]["walls"].add("W")
                    wall_count += 1
        
        return board
    
    def _place_robots_randomly(self):
        # Place robots in random positions
        positions = set()
        for color in self.robots:
            while True:
                x = random.randint(0, self.GRID_SIZE-1)
                y = random.randint(0, self.GRID_SIZE-1)
                
                # Avoid central square and duplicates
                if ((x, y) not in positions and 
                    not (7 <= x <= 8 and 7 <= y <= 8)):
                    self.robots[color]["pos"] = (x, y)
                    positions.add((x, y))
                    break
        
        # Store initial positions
        self.initial_positions = {color: robot["pos"] for color, robot in self.robots.items()}
    
    def _set_random_target(self):
        colors = list(self.robots.keys())
        self.current_target["color"] = random.choice(colors)
        
        # Find a position for the target that's not where a robot is
        robot_positions = {self.robots[color]["pos"] for color in self.robots}
        
        while True:
            x = random.randint(0, self.GRID_SIZE-1)
            y = random.randint(0, self.GRID_SIZE-1)
            
            # Avoid central square and robot positions
            if ((x, y) not in robot_positions and 
                not (7 <= x <= 8 and 7 <= y <= 8)):
                self.current_target["pos"] = (x, y)
                break
    
    def draw_board(self):
        self.canvas.delete("all")
    
        # Draw grid
        for i in range(self.GRID_SIZE+1):
            # Horizontal lines
            self.canvas.create_line(
                0, i * self.CELL_SIZE, 
                self.GRID_SIZE * self.CELL_SIZE, i * self.CELL_SIZE,
                fill=self.COLORS["grid"], width=1
            )

            # Vertical lines
            self.canvas.create_line(
                i * self.CELL_SIZE, 0,
                i * self.CELL_SIZE, self.GRID_SIZE * self.CELL_SIZE,
                fill=self.COLORS["grid"], width=1
            )

        # Draw the outer border explicitly
        self.canvas.create_rectangle(
            0, 0, 
            self.GRID_SIZE * self.CELL_SIZE, self.GRID_SIZE * self.CELL_SIZE,
            outline=self.COLORS["wall"], width=self.WALL_WIDTH
        )

        # Draw walls
        for x in range(self.GRID_SIZE):
            for y in range(self.GRID_SIZE):
                cell = self.board[x][y]

                if "N" in cell["walls"]:
                    self.canvas.create_line(
                        y * self.CELL_SIZE, x * self.CELL_SIZE,  
                        (y + 1) * self.CELL_SIZE, x * self.CELL_SIZE,  
                        fill=self.COLORS["wall"], width=self.WALL_WIDTH
                    )

                if "S" in cell["walls"]:
                    self.canvas.create_line(
                        y * self.CELL_SIZE, (x + 1) * self.CELL_SIZE,
                        (y + 1) * self.CELL_SIZE, (x + 1) * self.CELL_SIZE,
                        fill=self.COLORS["wall"], width=self.WALL_WIDTH
                    )

                if "W" in cell["walls"]:
                    self.canvas.create_line(
                        y * self.CELL_SIZE, x * self.CELL_SIZE,  # Top point of west wall
                        y * self.CELL_SIZE, (x + 1) * self.CELL_SIZE,  # Bottom point of west wall
                        fill=self.COLORS["wall"], width=self.WALL_WIDTH
                    )

                if "E" in cell["walls"]:
                    self.canvas.create_line(
                        (y + 1) * self.CELL_SIZE, x * self.CELL_SIZE,
                        (y + 1) * self.CELL_SIZE, (x + 1) * self.CELL_SIZE,
                        fill=self.COLORS["wall"], width=self.WALL_WIDTH
                    )

        # Draw central square
        self.canvas.create_rectangle(
            7 * self.CELL_SIZE, 7 * self.CELL_SIZE,
            9 * self.CELL_SIZE, 9 * self.CELL_SIZE,
            fill="#BBBBBB", outline=self.COLORS["wall"], width=self.WALL_WIDTH
        )
        
        # Draw target
        tx, ty = self.current_target["pos"]
        target_color = self.current_target["color"]
        
        self.canvas.create_oval(
            ty * self.CELL_SIZE + 10, tx * self.CELL_SIZE + 10,
            (ty + 1) * self.CELL_SIZE - 10, (tx + 1) * self.CELL_SIZE - 10,
            fill=self.COLORS["target"], outline=self.COLORS["robots"][target_color], width=3
        )
        
        # Draw robots
        for color, robot in self.robots.items():
            x, y = robot["pos"]
            outline_width = 3 if robot["selected"] else 1
            
            self.canvas.create_oval(
                y * self.CELL_SIZE + (self.CELL_SIZE - 2*self.ROBOT_RADIUS) // 2,
                x * self.CELL_SIZE + (self.CELL_SIZE - 2*self.ROBOT_RADIUS) // 2,
                y * self.CELL_SIZE + self.CELL_SIZE - (self.CELL_SIZE - 2*self.ROBOT_RADIUS) // 2,
                x * self.CELL_SIZE + self.CELL_SIZE - (self.CELL_SIZE - 2*self.ROBOT_RADIUS) // 2,
                fill=self.COLORS["robots"][color],
                outline="white",
                width=outline_width,
                tags=f"robot_{color}"
            )
        
        # Update UI labels
        self.moves_label.config(text=f"Moves: {self.moves_count}")
        self.target_label.config(text=f"Target: {self.current_target['color'].capitalize()}")
        
        if self.best_solution != float('inf'):
            self.best_label.config(text=f"Best: {self.best_solution}")
        else:
            self.best_label.config(text="Best: --")
    
    def move_robot(self, color, direction):
        """
        Move the robot in the specified direction until it hits a wall or another robot.
        
        Args:
            color (str): The color of the robot to move
            direction (str): 'N', 'S', 'E', or 'W' for North, South, East, or West
            
        Returns:
            bool: True if the robot moved, False otherwise
        """
        robot = self.robots[color]
        x, y = robot["pos"]
        
        # Determine the target position based on direction
        dx, dy = 0, 0
        if direction == "N":
            dx = -1
        elif direction == "S":
            dx = 1
        elif direction == "W":
            dy = -1
        elif direction == "E":
            dy = 1
        
        # Move the robot until it hits a wall or another robot
        new_x, new_y = x, y
        while True:
            # Check for walls in current cell for the direction we're moving
            if direction in self.board[new_x][new_y]["walls"]:
                break
            
            # Calculate next position
            next_x, next_y = new_x + dx, new_y + dy
            
            # Check for board boundaries
            if not (0 <= next_x < self.GRID_SIZE and 0 <= next_y < self.GRID_SIZE):
                break
            
            # Check for wall in the next cell (opposite direction)
            opposite_direction = {"N": "S", "S": "N", "E": "W", "W": "E"}[direction]
            if opposite_direction in self.board[next_x][next_y]["walls"]:
                break
            
            # Check for other robots
            robot_positions = {self.robots[c]["pos"] for c in self.robots if c != color}
            if (next_x, next_y) in robot_positions:
                break
            
            # Move to next position
            new_x, new_y = next_x, next_y
        
        # Update robot position if it moved
        if (new_x, new_y) != (x, y):
            robot["pos"] = (new_x, new_y)
            self.moves_count += 1
            self.draw_board()
            
            # Check if target is reached
            if (self.current_target["color"] == color and 
                robot["pos"] == self.current_target["pos"]):
                self._handle_win()
            
            return True
        return False
    
    def _handle_win(self):
        """Handle winning the game - stop timer, update best score, and show message"""
        # Stop timer
        self.timer_running = False
        
        # Update best solution if current is better
        if self.moves_count < self.best_solution:
            self.best_solution = self.moves_count
        
        messagebox.showinfo("Success!", 
                          f"Target reached in {self.moves_count} moves!\n"
                          f"Time: {self._format_time(self.elapsed_time)}")
        
        # Ask if player wants a new game
        if messagebox.askyesno("New Game", "Start a new game?"):
            self.new_game()
    
    def new_game(self):
        """Start a completely new game with new board, robots, and target"""
        self.board = self._create_board()
        self._place_robots_randomly()
        self._set_random_target()
        self.moves_count = 0
        
        # Reset timer
        self.timer_running = True
        self.start_time = time.time()
        self.elapsed_time = 0
        self._update_timer()
        
        # Deselect all robots
        for color in self.robots:
            self.robots[color]["selected"] = False
        
        # Reset solver state
        self.solution_moves = []
        self.is_showing_solution = False
        
        self.draw_board()
    
    def reset_positions(self):
        """Reset robots to their initial positions for the current game"""
        for color, pos in self.initial_positions.items():
            self.robots[color]["pos"] = pos
            self.robots[color]["selected"] = False
        
        self.moves_count = 0
        
        # Reset timer
        self.timer_running = True
        self.start_time = time.time()
        self.elapsed_time = 0
        self._update_timer()
        
        # Reset solver state
        self.solution_moves = []
        self.is_showing_solution = False
        
        self.draw_board()
    
    def reset_game(self):
        """Randomize robot positions but keep the same board and target"""
        self._place_robots_randomly()
        self.moves_count = 0
        
        # Reset timer
        self.timer_running = True
        self.start_time = time.time()
        self.elapsed_time = 0
        self._update_timer()
        
        # Deselect all robots
        for color in self.robots:
            self.robots[color]["selected"] = False
        
        # Reset solver state
        self.solution_moves = []
        self.is_showing_solution = False
        
        self.draw_board()
    
    def give_up(self):
        """Give up the current game"""
        # Stop timer
        self.timer_running = False
        
        if messagebox.askyesno("Give Up", "Are you sure you want to give up?"):
            messagebox.showinfo("Game Over", "Better luck next time!")
            self.new_game()
    
    def on_canvas_click(self, event):
        """Handle clicks on the game canvas, typically to select a robot"""
        # Calculate grid position
        col = event.x // self.CELL_SIZE
        row = event.y // self.CELL_SIZE
        
        # Check if a robot was clicked
        robot_clicked = None
        for color, robot in self.robots.items():
            rx, ry = robot["pos"]
            if (rx == row and ry == col):
                robot_clicked = color
                break
        
        if robot_clicked:
            # Deselect all robots
            for color in self.robots:
                self.robots[color]["selected"] = False
            
            # Select the clicked robot
            self.robots[robot_clicked]["selected"] = True
            self.draw_board()
    
    def on_key_press(self, event):
        """Handle keyboard arrow key presses for moving robots"""
        key = event.keysym.upper()
        selected_robot = None
        
        # Find selected robot
        for color, robot in self.robots.items():
            if robot["selected"]:
                selected_robot = color
                break
        
        if selected_robot:
            # Handle arrow keys
            direction = None
            if key == "UP":
                direction = "N"
            elif key == "DOWN":
                direction = "S"
            elif key == "LEFT":
                direction = "W"
            elif key == "RIGHT":
                direction = "E"
            
            if direction:
                self.move_robot(selected_robot, direction)
    
    def _update_timer(self):
        """Update the timer display"""
        if self.timer_running:
            self.elapsed_time = time.time() - self.start_time
            self.timer_label.config(text=self._format_time(self.elapsed_time))
            self.root.after(1000, self._update_timer)
    
    def _format_time(self, seconds):
        """Format seconds as MM:SS"""
        minutes = int(seconds) // 60
        seconds = int(seconds) % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def solve_game(self):
        """Find and display the solution to the current game"""
        # Stop any existing solution animation
        if self.is_showing_solution:
            self.is_showing_solution = False
            messagebox.showinfo("Solution Cancelled", "Solution animation stopped.")
            return
        
        # Reset to initial positions
        self.reset_positions()
        
        # Find solution
        solution = self._find_solution()
        
        if solution:
            # We have a solution
            self.solution_moves = solution
            self.is_showing_solution = True
            self.solution_step_index = 0
            
            # Start showing the solution
            messagebox.showinfo("Solution Found", 
                               f"Solution found in {len(solution)} moves.\nWatching the solution...")
            self._show_next_solution_step()
        else:
            messagebox.showerror("No Solution", "Could not find a solution within a reasonable time.")
    
    def _show_next_solution_step(self):
        """Show the next step in the solution animation"""
        if not self.is_showing_solution or self.solution_step_index >= len(self.solution_moves):
            self.is_showing_solution = False
            return
        
        # Get the next move
        move = self.solution_moves[self.solution_step_index]
        color, direction = move
        
        # Select the robot
        for c in self.robots:
            self.robots[c]["selected"] = (c == color)
        
        # Move the robot
        self.move_robot(color, direction)
        
        # Increment step index
        self.solution_step_index += 1
        
        # Schedule next step with a delay
        self.root.after(500, self._show_next_solution_step)
    
    def _find_solution(self):
        """
        Find a solution using Breadth-First Search.
        
        Returns:
            list: List of (color, direction) moves to solve the puzzle, or None if no solution is found
        """
        target_color = self.current_target["color"]
        target_pos = self.current_target["pos"]
        
        # Create a BFS queue
        q = queue.Queue()
        
        # Store state as (robot positions dict, moves list)
        initial_positions = {color: robot["pos"] for color, robot in self.robots.items()}
        q.put((initial_positions, []))
        
        # Keep track of visited states to avoid loops
        visited = set()
        visited_key = self._get_state_key(initial_positions)
        visited.add(visited_key)
        
        # BFS with a maximum depth to avoid infinite loops or excessive computation
        max_depth = 20  # Limit the search depth
        
        while not q.empty():
            positions, moves = q.get()
            
            # Check if we've reached the target
            if positions[target_color] == target_pos:
                return moves
            
            # Stop if we've reached the maximum depth
            if len(moves) >= max_depth:
                continue
            
            # Try moving each robot in each direction
            for color in positions:
                for direction in ["N", "S", "E", "W"]:
                    # Create a temporary game state to simulate the move
                    temp_positions = positions.copy()
                    temp_robots = {c: {"pos": p, "selected": False} for c, p in temp_positions.items()}
                    
                    # Simulate the move
                    new_pos = self._simulate_move(temp_robots, color, direction)
                    
                    if new_pos != temp_positions[color]:
                        # The robot moved, so create a new state
                        temp_positions[color] = new_pos
                        new_state_key = self._get_state_key(temp_positions)
                        
                        if new_state_key not in visited:
                            visited.add(new_state_key)
                            new_moves = moves.copy()
                            new_moves.append((color, direction))
                            q.put((temp_positions, new_moves))
        
        # If we get here, no solution was found
        return None
    
    def _simulate_move(self, robots, color, direction):
        """
        Simulate moving a robot without changing the actual game state.
        
        Args:
            robots (dict): Dictionary of temporary robot positions
            color (str): The color of the robot to move
            direction (str): Direction to move ('N', 'S', 'E', 'W')
            
        Returns:
            tuple: The new position after the move
        """
        robot = robots[color]
        x, y = robot["pos"]
        
        # Determine the target position based on direction
        dx, dy = 0, 0
        if direction == "N":
            dx = -1
        elif direction == "S":
            dx = 1
        elif direction == "W":
            dy = -1
        elif direction == "E":
            dy = 1
        
        # Move the robot until it hits a wall or another robot
        new_x, new_y = x, y
        while True:
            # Check for walls in current cell for the direction we're moving
            if direction in self.board[new_x][new_y]["walls"]:
                break
            
            # Calculate next position
            next_x, next_y = new_x + dx, new_y + dy
            
            # Check for board boundaries
            if not (0 <= next_x < self.GRID_SIZE and 0 <= next_y < self.GRID_SIZE):
                break
            
            # Check for wall in the next cell (opposite direction)
            opposite_direction = {"N": "S", "S": "N", "E": "W", "W": "E"}[direction]
            if opposite_direction in self.board[next_x][next_y]["walls"]:
                break
            
            # Check for other robots
            robot_positions = {robots[c]["pos"] for c in robots if c != color}
            if (next_x, next_y) in robot_positions:
                break
            
            # Move to next position
            new_x, new_y = next_x, next_y
        
        return (new_x, new_y)
    
    def _get_state_key(self, positions):
        """
        Generate a unique key for a game state based on robot positions.
        
        Args:
            positions (dict): Dictionary of robot positions
            
        Returns:
            tuple: A hashable tuple representing the game state
        """
        # Sort by color to ensure consistent ordering
        return tuple((color, positions[color]) for color in sorted(positions.keys()))

if __name__ == "__main__":
    root = tk.Tk()
    game = RicochetRobotsGame(root)
    root.mainloop()