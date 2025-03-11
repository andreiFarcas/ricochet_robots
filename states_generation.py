from ui import RicochetRobotsGame   # Import the game logic and UI elements

import tkinter as tk                # Import the tkinter library for the GUI
import copy                         # Import the copy library to make deep copies of objects
import threading                    # Import the threading library to run the AI in a separate thread

class RicochetRobotsAI:
    def __init__(self):
        # Create the root window
        self.root = tk.Tk()
        self.game = RicochetRobotsGame(self.root) # Create a new game instance
        
        # Start UI in a separate thread
        self.ui_thread = threading.Thread(target=self.run_ui)
        self.ui_thread.daemon = True  # This ensures the thread will close when the main program exits
        self.ui_thread.start()
        
        # Give the UI a moment to initialize
        self.root.after(500, self.root.update)
    
    def run_ui(self):
        try:
            self.root.mainloop()
        except Exception as e:
            print(f"UI thread error: {e}")

    def ai_stuff_needed(self):
        """
            Currently this only generates the possible states from the current game state
            and prints the robot positions in the new states
        """

        # Take the current game state
        game_state = self.game.get_game_state()

                # DEBUG: Print the current board
        print("Current board: ")
        for row in self.game.board:
            print(row)

        # Generate all possible states from the current game state
        new_states = self.generate_states(game_state)

        # Print the positions of the robots in the new states
        for i, state in enumerate(new_states):
            print("New state", i, ": ")
            for robot in state["robots"]:
                print("\t", robot, "robot position: ", state["robots"][robot]["pos"])

    # Helper function to check if a move is valid
    def is_valid_move(self, board, x, y, direction, robots):
        # Check if the robot can move in the given direction from the given square
        if direction == "N" and "N" not in board[x][y]["walls"] and (x, y - 1) not in robots:
            return True
        elif direction == "S" and "S" not in board[x][y]["walls"] and (x, y + 1) not in robots:
            return True
        elif direction == "W" and "W" not in board[x][y]["walls"] and (x - 1, y) not in robots:
            return True
        elif direction == "E" and "E" not in board[x][y]["walls"] and (x + 1, y) not in robots:
            return True
        return False


    def move_robot(self, robot, direction, state):
        """
        Moves the robot in the given direction
        """
        board = state["board"]
        robots = state["robots"]
        x, y = robots[robot]['pos']

        if direction == "N":
            print("Moving robot", robot, "North")
            while True:
                # Check if we're at the edge of the board
                if x <= 0:
                    break

                # Check if the current cell has a north wall
                if "N" in board[x][y]["walls"]:
                    break

                # Check if the northern cell has a south wall
                if x > 0 and "S" in board[x-1][y]["walls"]:
                    break

                # Check if there's a robot in the northern cell
                if (x - 1, y) in [r['pos'] for r in robots.values()]:
                    break

                # If all checks pass, move north
                x -= 1
                print("Next iteration wall check for square: (", x, ",", y, ") is:", board[x][y]["walls"])

        elif direction == "S":
            print("Moving robot", robot, "South")
            while True:
                # Check if we're at the edge of the board
                if x >= 15:
                    break

                # Check if the current cell has a south wall
                if "S" in board[x][y]["walls"]:
                    break

                # Check if the southern cell has a north wall
                if x < 15 and "N" in board[x+1][y]["walls"]:
                    break

                # Check if there's a robot in the southern cell
                if (x + 1, y) in [r['pos'] for r in robots.values()]:
                    break

                # If all checks pass, move south
                x += 1

        elif direction == "W":
            print("Moving robot", robot, "West")
            while True:
                # Check if we're at the edge of the board
                if y <= 0:
                    break

                # Check if the current cell has a west wall
                if "W" in board[x][y]["walls"]:
                    break

                # Check if the western cell has an east wall
                if y > 0 and "E" in board[x][y-1]["walls"]:
                    break

                # Check if there's a robot in the western cell
                if (x, y - 1) in [r['pos'] for r in robots.values()]:
                    break

                # If all checks pass, move west
                y -= 1

        elif direction == "E":
            print("Moving robot", robot, "East")
            while True:
                # Check if we're at the edge of the board
                if y >= 15:
                    break

                # Check if the current cell has an east wall
                if "E" in board[x][y]["walls"]:
                    break

                # Check if the eastern cell has a west wall
                if y < 15 and "W" in board[x][y+1]["walls"]:
                    break

                # Check if there's a robot in the eastern cell
                if (x, y + 1) in [r['pos'] for r in robots.values()]:
                    break

                # If all checks pass, move east
                y += 1

        return (x, y)

    def generate_states(self, game_state):
        """
        Generates all possible states from the current game state
        """
        # Get the current board and robot positions
        board = game_state["board"]
        robots = game_state["robots"]

        # Generate all possible moves for each robot
        new_states = []
        for robot in robots:
            x, y = robots[robot]['pos']
            for direction in ["N", "S", "W", "E"]:
                if self.is_valid_move(board, x, y, direction, robots):
                    # Make a copy of the game state and update the robot position
                    new_game_state = copy.deepcopy(game_state)
                    new_game_state["robots"][robot]["pos"] = self.move_robot(robot, direction, new_game_state)
                    new_states.append(new_game_state)
                    print("New state: ")
                    for robot in new_game_state["robots"]:
                        print("\t", robot, "robot position: ", new_game_state["robots"][robot]["pos"])


        return new_states

            
if __name__ == "__main__":
    ai = RicochetRobotsAI()
    ai.ai_stuff_needed()  # Call ai_stuff_needed (now it will only print the possible states from current one)
    
    # Keep the main thread alive to see the UI
    while True:
        try:
            user_input = input("Press Enter to run analysis again, or type 'exit' to quit: ")
            if user_input.lower() == 'exit':
                break
            ai.ai_stuff_needed()
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
            break