# Ricochet Robots Game

## Overview
Ricochet Robots is a puzzle game where players maneuver robots on a grid to reach a target position. The game features a unique mechanic where robots move in straight lines until they hit a wall or another robot. The objective is to find the optimal sequence of moves to get the designated robot to the target position.

## Project Structure
The project consists of the following files:

- **ui_v5.py**: Contains all the UI elements for the Ricochet Robots game. It defines the `RicochetRobotsGame` class, which includes methods for initializing the game window, creating the game board, handling user interactions, and updating the display. It manages the layout, buttons, labels, and canvas for the game interface.

- **manhattan_a_star.py**: Contains the AI solver code for the Ricochet Robots game. It includes methods for finding a solution to the game using the A* search algorithm and a simple heuristic based on Manhattan distance. The file also defines managing game states, and generating moves to solve the puzzle.

- **reachability_a_star**: An improvement of the solver based on Manhattan distance. Uses a new heuristic that precomputes a reachability matrix from the target to all reachable locations by using a BFS and ignoring the rest of the robots.

## How to Run the Game
1. Ensure you have Python installed on your machine.
2. Clone the repository or download the project files.
3. Navigate to the project directory in your terminal.
4. Run the game using the following command:
   ```
   python ui_v5.py
   ```
5. Follow the on-screen instructions to play the game.

## Features
- Interactive UI for selecting robots and moving them using arrow keys.
- Randomized game board with walls and targets.
- AI solvers that can find the optimal solution using the A* search algorithm.
- Timer to track the duration of the game.
- Option to reset positions and start new games.

## License
This project is licensed under the MIT License. Feel free to modify and distribute as needed.