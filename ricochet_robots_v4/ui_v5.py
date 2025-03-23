import tkinter as tk
from tkinter import messagebox, ttk
import random
import time
import threading


from manhattan_a_star import AStarSolver
from reachability_a_star import ReachabilityAStarSolver

class RicochetRobotsGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Ricochet Robots v5")
        self.root.geometry("1000x720")
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
        
        # Solver state (UI animation)
        self.solution_moves = []
        self.is_showing_solution = False
        self.solution_step_index = 0
        
        # Create main layout frames
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.left_frame = tk.Frame(self.main_frame)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.right_frame = tk.Frame(self.main_frame, width=220)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        self.right_frame.pack_propagate(False)
        
        # Game board canvas
        self.canvas_frame = tk.Frame(self.left_frame)
        self.canvas_frame.pack(pady=10)
        
        self.canvas = tk.Canvas(
            self.canvas_frame, 
            width=self.GRID_SIZE * self.CELL_SIZE,
            height=self.GRID_SIZE * self.CELL_SIZE, 
            bg=self.COLORS["background"]
        )
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
        
        self.timer_frame = tk.Frame(self.right_frame, relief=tk.GROOVE, bd=2)
        self.timer_frame.pack(fill=tk.X, pady=10)
        
        self.timer_title = tk.Label(self.timer_frame, text="Time", font=("Arial", 12))
        self.timer_title.pack(pady=(5, 0))
        
        self.timer_label = tk.Label(self.timer_frame, text="00:00", font=("Arial", 20, "bold"))
        self.timer_label.pack(pady=(0, 5))
        
        # Game control buttons
        self.control_frame = tk.Frame(self.right_frame)
        self.control_frame.pack(fill=tk.X, pady=10)
        
        self.new_game_btn = tk.Button(
            self.control_frame, text="New Game", command=self.new_game,
            font=("Arial", 12), bg="#4CAF50", fg="white", height=2
        )
        self.new_game_btn.pack(fill=tk.X, pady=(0, 5))
        
        self.reset_pos_btn = tk.Button(
            self.control_frame, text="Reset Positions", command=self.reset_positions,
            font=("Arial", 12), bg="#2196F3", fg="white", height=2
        )
        self.reset_pos_btn.pack(fill=tk.X, pady=5)
        
        self.reset_game_btn = tk.Button(
            self.control_frame, text="Reset Game", command=self.reset_game,
            font=("Arial", 12), bg="#FF9800", fg="white", height=2
        )
        self.reset_game_btn.pack(fill=tk.X, pady=5)
        
        # Solver buttons - new section with label
        self.solver_frame = tk.LabelFrame(self.right_frame, text="Solvers", font=("Arial", 12))
        self.solver_frame.pack(fill=tk.X, pady=10)
        
        self.manhattan_solve_btn = tk.Button(
            self.solver_frame, text="A* (Manhattan)", command=lambda: self.solve_game("manhattan"),
            font=("Arial", 11), bg="#9C27B0", fg="white", height=1
        )
        self.manhattan_solve_btn.pack(fill=tk.X, pady=5, padx=5)
        
        self.reachability_solve_btn = tk.Button(
            self.solver_frame, text="A* (Reachability)", command=lambda: self.solve_game("reachability"),
            font=("Arial", 11), bg="#673AB7", fg="white", height=1
        )
        self.reachability_solve_btn.pack(fill=tk.X, pady=5, padx=5)
        
        self.give_up_btn = tk.Button(
            self.control_frame, text="Give Up", command=self.give_up,
            font=("Arial", 12), bg="#F44336", fg="white", height=2
        )
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
            "5. Click a solver button\n   to see a solution"
        )
        self.instructions_label = tk.Label(
            self.instructions_frame, text=instructions_text, 
            font=("Arial", 10), justify=tk.LEFT
        )
        self.instructions_label.pack(pady=5, padx=0)
        
        # Bind events
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.root.bind("<KeyPress>", self.on_key_press)
        
        # Initialize game
        self.new_game()
    
    def _create_board(self):
        # ...existing code...
        board = [[{"walls": set()} for _ in range(self.GRID_SIZE)] for _ in range(self.GRID_SIZE)]
        # Outer walls
        for i in range(self.GRID_SIZE):
            board[0][i]["walls"].add("N")
            board[self.GRID_SIZE - 1][i]["walls"].add("S")
            board[i][0]["walls"].add("W")
            board[i][self.GRID_SIZE - 1]["walls"].add("E")
        # Central square walls
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
        # Random internal walls (~40)
        wall_count = 0
        while wall_count < 40:
            x = random.randint(0, self.GRID_SIZE - 2)
            y = random.randint(0, self.GRID_SIZE - 2)
            if random.choice([True, False]):
                if "S" not in board[x][y]["walls"] and "N" not in board[x][y + 1]["walls"]:
                    board[x][y]["walls"].add("S")
                    board[x][y + 1]["walls"].add("N")
                    wall_count += 1
            else:
                if "E" not in board[x][y]["walls"] and "W" not in board[x + 1][y]["walls"]:
                    board[x][y]["walls"].add("E")
                    board[x + 1][y]["walls"].add("W")
                    wall_count += 1
        return board
    
    def _place_robots_randomly(self):
        positions = set()
        for color in self.robots:
            while True:
                x = random.randint(0, self.GRID_SIZE - 1)
                y = random.randint(0, self.GRID_SIZE - 1)
                if ((x, y) not in positions and not (7 <= x <= 8 and 7 <= y <= 8)):
                    self.robots[color]["pos"] = (x, y)
                    positions.add((x, y))
                    break
        self.initial_positions = {color: robot["pos"] for color, robot in self.robots.items()}
    
    def _set_random_target(self):
        colors = list(self.robots.keys())
        self.current_target["color"] = random.choice(colors)
        robot_positions = {self.robots[color]["pos"] for color in self.robots}
        while True:
            x = random.randint(0, self.GRID_SIZE - 1)
            y = random.randint(0, self.GRID_SIZE - 1)
            if ((x, y) not in robot_positions and not (7 <= x <= 8 and 7 <= y <= 8)):
                self.current_target["pos"] = (x, y)
                break
    
    def draw_board(self):
        self.canvas.delete("all")
        
        # Draw grid lines
        for i in range(self.GRID_SIZE + 1):
            self.canvas.create_line(
                0, i * self.CELL_SIZE,
                self.GRID_SIZE * self.CELL_SIZE, i * self.CELL_SIZE,
                fill=self.COLORS["grid"], width=1
            )
            self.canvas.create_line(
                i * self.CELL_SIZE, 0,
                i * self.CELL_SIZE, self.GRID_SIZE * self.CELL_SIZE,
                fill=self.COLORS["grid"], width=1
            )
        
        # Draw outer borders with equal thickness
        full_width = self.WALL_WIDTH  # Use full width for all borders
        half_width = full_width / 2
        
        # Top border - centered on the edge
        self.canvas.create_line(
            0, half_width, 
            self.GRID_SIZE * self.CELL_SIZE, half_width,
            fill=self.COLORS["wall"], width=full_width
        )
        
        # Bottom border - centered on the edge
        self.canvas.create_line(
            0, self.GRID_SIZE * self.CELL_SIZE, 
            self.GRID_SIZE * self.CELL_SIZE, self.GRID_SIZE * self.CELL_SIZE - half_width,
            fill=self.COLORS["wall"], width=full_width / 2
        )
        
        # Left border - centered on the edge
        self.canvas.create_line(
            half_width, 0, 
            half_width, self.GRID_SIZE * self.CELL_SIZE,
            fill=self.COLORS["wall"], width=full_width
        )
        
        # Right border - centered on the edge
        self.canvas.create_line(
            self.GRID_SIZE * self.CELL_SIZE, 0,
            self.GRID_SIZE * self.CELL_SIZE, self.GRID_SIZE * self.CELL_SIZE,
            fill=self.COLORS["wall"], width=full_width / 2
        )
        
        # Draw walls for each cell
        for x in range(self.GRID_SIZE):
            for y in range(self.GRID_SIZE):
                cell = self.board[x][y]
                if "N" in cell["walls"] and x > 0:  # Skip drawing N walls for the top row (already drawn)
                    self.canvas.create_line(
                        y * self.CELL_SIZE, x * self.CELL_SIZE,
                        (y + 1) * self.CELL_SIZE, x * self.CELL_SIZE,
                        fill=self.COLORS["wall"], width=self.WALL_WIDTH
                    )
                if "S" in cell["walls"] and x < self.GRID_SIZE - 1:  # Skip drawing S walls for the bottom row
                    self.canvas.create_line(
                        y * self.CELL_SIZE, (x + 1) * self.CELL_SIZE,
                        (y + 1) * self.CELL_SIZE, (x + 1) * self.CELL_SIZE,
                        fill=self.COLORS["wall"], width=self.WALL_WIDTH
                    )
                if "W" in cell["walls"] and y > 0:  # Skip drawing W walls for the leftmost column
                    self.canvas.create_line(
                        y * self.CELL_SIZE, x * self.CELL_SIZE,
                        y * self.CELL_SIZE, (x + 1) * self.CELL_SIZE,
                        fill=self.COLORS["wall"], width=self.WALL_WIDTH
                    )
                if "E" in cell["walls"] and y < self.GRID_SIZE - 1:  # Skip drawing E walls for the rightmost column
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
            fill=self.COLORS["target"],
            outline=self.COLORS["robots"][target_color], width=3
        )
        
        # Draw robots
        for color, robot in self.robots.items():
            x, y = robot["pos"]
            outline_width = 3 if robot["selected"] else 1
            self.canvas.create_oval(
                y * self.CELL_SIZE + (self.CELL_SIZE - 2 * self.ROBOT_RADIUS) // 2,
                x * self.CELL_SIZE + (self.CELL_SIZE - 2 * self.ROBOT_RADIUS) // 2,
                y * self.CELL_SIZE + self.CELL_SIZE - (self.CELL_SIZE - 2 * self.ROBOT_RADIUS) // 2,
                x * self.CELL_SIZE + self.CELL_SIZE - (self.CELL_SIZE - 2 * self.ROBOT_RADIUS) // 2,
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
        robot = self.robots[color]
        x, y = robot["pos"]
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
            if direction in self.board[new_x][new_y]["walls"]:
                break
            next_x, next_y = new_x + dx, new_y + dy
            if not (0 <= next_x < self.GRID_SIZE and 0 <= next_y < self.GRID_SIZE):
                break
            opposite = {"N": "S", "S": "N", "E": "W", "W": "E"}[direction]
            if opposite in self.board[next_x][next_y]["walls"]:
                break
            robot_positions = {self.robots[c]["pos"] for c in self.robots if c != color}
            if (next_x, next_y) in robot_positions:
                break
            new_x, new_y = next_x, next_y
        if (new_x, new_y) != (x, y):
            robot["pos"] = (new_x, new_y)
            self.moves_count += 1
            self.draw_board()
            if self.current_target["color"] == color and robot["pos"] == self.current_target["pos"]:
                self._handle_win()
            return True
        return False
    
    def _handle_win(self):
        self.timer_running = False
        if self.moves_count < self.best_solution:
            self.best_solution = self.moves_count
        messagebox.showinfo("Success!",
                            f"Target reached in {self.moves_count} moves!\n"
                            f"Time: {self._format_time(self.elapsed_time)}")
        if messagebox.askyesno("New Game", "Start a new game?"):
            self.new_game()
    
    def new_game(self):
        self.board = self._create_board()
        self._place_robots_randomly()
        self._set_random_target()
        self.moves_count = 0
        self.timer_running = True
        self.start_time = time.time()
        self.elapsed_time = 0
        self._update_timer()
        for color in self.robots:
            self.robots[color]["selected"] = False
        self.solution_moves = []
        self.is_showing_solution = False
        self.draw_board()
    
    def reset_positions(self):
        for color, pos in self.initial_positions.items():
            self.robots[color]["pos"] = pos
            self.robots[color]["selected"] = False
        self.moves_count = 0
        self.timer_running = True
        self.start_time = time.time()
        self.elapsed_time = 0
        self._update_timer()
        self.solution_moves = []
        self.is_showing_solution = False
        self.draw_board()
    
    def reset_game(self):
        self._place_robots_randomly()
        self.moves_count = 0
        self.timer_running = True
        self.start_time = time.time()
        self.elapsed_time = 0
        self._update_timer()
        for color in self.robots:
            self.robots[color]["selected"] = False
        self.solution_moves = []
        self.is_showing_solution = False
        self.draw_board()
    
    def give_up(self):
        self.timer_running = False
        if messagebox.askyesno("Give Up", "Are you sure you want to give up?"):
            messagebox.showinfo("Game Over", "Better luck next time!")
            self.new_game()
    
    def on_canvas_click(self, event):
        col = event.x // self.CELL_SIZE
        row = event.y // self.CELL_SIZE
        robot_clicked = None
        for color, robot in self.robots.items():
            rx, ry = robot["pos"]
            if (rx == row and ry == col):
                robot_clicked = color
                break
        if robot_clicked:
            for color in self.robots:
                self.robots[color]["selected"] = False
            self.robots[robot_clicked]["selected"] = True
            self.draw_board()
    
    def on_key_press(self, event):
        key = event.keysym.upper()
        selected_robot = None
        for color, robot in self.robots.items():
            if robot["selected"]:
                selected_robot = color
                break
        if selected_robot:
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
        if self.timer_running:
            self.elapsed_time = time.time() - self.start_time
            self.timer_label.config(text=self._format_time(self.elapsed_time))
            self.root.after(1000, self._update_timer)
    
    def _format_time(self, seconds):
        minutes = int(seconds) // 60
        seconds = int(seconds) % 60
        return f"{minutes:02d}:{seconds:02d}"

    def solve_game(self, solver_type="manhattan"):
        """
        Solve the game using the specified solver.
        
        Args:
            solver_type (str): The type of solver to use: 'manhattan' or 'reachability'
        """
        if self.is_showing_solution:
            self.is_showing_solution = False
            messagebox.showinfo("Solution Cancelled", "Solution animation stopped.")
            return
        
        self.reset_positions()
        
        # Create and show the progress window
        progress_window = SolverProgressWindow(self.root, solver_type)
        
        # Prepare data for solver
        target_color = self.current_target["color"]
        target_pos = self.current_target["pos"]
        initial_positions = {color: robot["pos"] for color, robot in self.robots.items()}
        
        # Shared variables between threads
        solution_result = {"solution": None, "states_explored": 0}
        
        def solver_thread():
            """
            This function runs the selected solver in a separate thread to avoid blocking the UI.
            It also updates the progress window with the number of states explored.
            """
            # Create solver based on the type with a new callback for progress updates
            if solver_type == "manhattan":
                solver = AStarSolver(self.board, initial_positions, target_color, target_pos)
                
                def progress_callback(states_explored):
                    solution_result["states_explored"] = states_explored
                    self.root.after(100, lambda: progress_window.update_states(states_explored))
                    return not progress_window.cancelled
                
                # Run the solver with the callback
                solution = solver.a_star_search(progress_callback)
                
            elif solver_type == "reachability":
                solver = ReachabilityAStarSolver(self.board, initial_positions, target_color, target_pos)
                
                def progress_callback(states_explored):
                    solution_result["states_explored"] = states_explored
                    self.root.after(100, lambda: progress_window.update_states(states_explored))
                    return not progress_window.cancelled
                
                # Run the solver with the callback
                solution = solver.a_star_search(progress_callback)
            
            solution_result["solution"] = solution
            
            # When done, update the UI thread
            self.root.after(0, lambda: handle_solution_found(solution))
        
        def handle_solution_found(solution):
            # Close the progress window
            progress_window.close()
            
            # Process the solution
            if solution:
                self.solution_moves = solution
                self.is_showing_solution = True
                self.solution_step_index = 0
                messagebox.showinfo("Solution Found", 
                                  f"Solution found in {len(solution)} moves after exploring "
                                  f"{solution_result['states_explored']} states.\n"
                                  f"Watching the solution...")
                self._show_next_solution_step()
            else:
                if progress_window.cancelled:
                    messagebox.showinfo("Search Cancelled", "The solver was cancelled.")
                else:
                    messagebox.showerror("No Solution", 
                                       "Could not find a solution within the search limits.\n"
                                       f"Explored {solution_result['states_explored']} states.")
        
        # Start the solver in a separate thread
        solver_thread = threading.Thread(target=solver_thread)
        solver_thread.daemon = True  # This ensures the thread will exit when the main program exits
        solver_thread.start()

    def _show_next_solution_step(self):
        if not self.is_showing_solution or self.solution_step_index >= len(self.solution_moves):
            self.is_showing_solution = False
            return
        move = self.solution_moves[self.solution_step_index]
        color, direction = move
        for c in self.robots:
            self.robots[c]["selected"] = (c == color)
        self.move_robot(color, direction)
        self.solution_step_index += 1
        self.root.after(500, self._show_next_solution_step)

class SolverProgressWindow:
    def __init__(self, parent, solver_type="manhattan"):
        self.window = tk.Toplevel(parent)
        self.window.title(f"Solver Progress - {self._get_solver_name(solver_type)}")
        self.window.geometry("400x200")
        self.window.resizable(False, False)
        self.window.transient(parent)  # Make this window related to the parent
        self.window.grab_set()  # Make this window modal
        
        # Center the window on the parent
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        x = parent_x + (parent_width - 400) // 2
        y = parent_y + (parent_height - 200) // 2
        self.window.geometry(f"+{x}+{y}")
        
        # Status message
        self.status_var = tk.StringVar(value=f"Searching for a solution with {self._get_solver_name(solver_type)}...")
        self.status_label = tk.Label(self.window, textvariable=self.status_var, font=("Arial", 12))
        self.status_label.pack(pady=(20, 10))
        
        # Progress bar
        self.progress = ttk.Progressbar(self.window, mode="indeterminate", length=300)
        self.progress.pack(pady=10)
        self.progress.start()
        
        # Stats frame
        self.stats_frame = tk.Frame(self.window)
        self.stats_frame.pack(fill=tk.X, pady=10, padx=20)
        
        # Elapsed time
        self.time_var = tk.StringVar(value="Elapsed: 0s")
        self.time_label = tk.Label(self.stats_frame, textvariable=self.time_var, font=("Arial", 10))
        self.time_label.pack(side=tk.LEFT, padx=10)
        
        # States explored
        self.states_var = tk.StringVar(value="States: 0")
        self.states_label = tk.Label(self.stats_frame, textvariable=self.states_var, font=("Arial", 10))
        self.states_label.pack(side=tk.RIGHT, padx=10)
        
        # Cancel button
        self.cancel_btn = tk.Button(self.window, text="Cancel", command=self.cancel, 
                                   font=("Arial", 11), bg="#F44336", fg="white")
        self.cancel_btn.pack(pady=10)
        
        # Flag to track if the search was cancelled
        self.cancelled = False
        
        # Start the timer
        self.start_time = time.time()
        self.update_timer()
    
    def _get_solver_name(self, solver_type):
        if solver_type == "manhattan":
            return "Manhattan Heuristic"
        elif solver_type == "reachability":
            return "Reachability Heuristic"
        return "Unknown Solver"
    
    def update_timer(self):
        if not self.cancelled:
            elapsed = int(time.time() - self.start_time)
            self.time_var.set(f"Elapsed: {elapsed}s")
            self.window.after(1000, self.update_timer)
    
    def update_states(self, count):
        self.states_var.set(f"States: {count}")
    
    def set_status(self, text):
        self.status_var.set(text)
    
    def cancel(self):
        self.cancelled = True
        self.set_status("Cancelling...")
        # The parent window will check this flag
    
    def close(self):
        self.window.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    game = RicochetRobotsGame(root)
    root.mainloop()