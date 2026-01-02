import tkinter as tk
from tkinter import messagebox
import random
import heapq
import copy

# --- AI Solver Logic (A* Algorithm) ---

class PuzzleNode:
    def __init__(self, state, parent=None, move=None, g=0):
        self.state = state
        self.parent = parent
        self.move = move
        self.g = g  # Cost from start node
        self.h = self.calculate_manhattan()  # Heuristic cost
        self.f = self.g + self.h  # Total cost

    def calculate_manhattan(self):
        distance = 0
        for i in range(9):
            if self.state[i] == 0: continue
            val = self.state[i] - 1
            target_x, target_y = val % 3, val // 3
            current_x, current_y = i % 3, i // 3
            distance += abs(target_x - current_x) + abs(target_y - current_y)
        return distance

    def __lt__(self, other):
        return self.f < other.f

    def get_blank_index(self):
        return self.state.index(0)

    def get_neighbors(self):
        neighbors = []
        blank_idx = self.get_blank_index()
        row, col = blank_idx // 3, blank_idx % 3
        moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, Down, Left, Right

        for dr, dc in moves:
            nr, nc = row + dr, col + dc
            if 0 <= nr < 3 and 0 <= nc < 3:
                new_idx = nr * 3 + nc
                new_state = list(self.state)
                # Swap blank with neighbor
                new_state[blank_idx], new_state[new_idx] = new_state[new_idx], new_state[blank_idx]
                neighbors.append(PuzzleNode(tuple(new_state), self, (dr, dc), self.g + 1))
        return neighbors

def solve_puzzle_astar(start_state):
    goal_state = (1, 2, 3, 4, 5, 6, 7, 8, 0)
    start_node = PuzzleNode(tuple(start_state))
    
    if start_state == goal_state:
        return []

    open_list = []
    heapq.heappush(open_list, start_node)
    visited = set()
    visited.add(tuple(start_state))

    while open_list:
        current_node = heapq.heappop(open_list)

        if current_node.state == goal_state:
            path = []
            while current_node.parent:
                path.append(current_node.state)
                current_node = current_node.parent
            return path[::-1] # Return reversed path

        for neighbor in current_node.get_neighbors():
            if neighbor.state not in visited:
                visited.add(neighbor.state)
                heapq.heappush(open_list, neighbor)
    return None

# --- GUI Application ---

class PuzzleGameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("8-Puzzle AI Game")
        self.root.geometry("400x550")
        self.root.configure(bg="#f0f0f0")

        self.steps = 0
        self.current_state = []
        
        # UI Elements
        self.label_title = tk.Label(root, text="8-Puzzle Game", font=("Helvetica", 24, "bold"), bg="#f0f0f0")
        self.label_title.pack(pady=10)

        self.label_steps = tk.Label(root, text=f"Steps: {self.steps}", font=("Helvetica", 14), bg="#f0f0f0")
        self.label_steps.pack(pady=5)

        self.frame_board = tk.Frame(root, bg="#333", padx=5, pady=5)
        self.frame_board.pack(pady=10)

        self.buttons = []
        for i in range(9):
            btn = tk.Button(self.frame_board, text="", font=("Helvetica", 20, "bold"), width=4, height=2,
                            command=lambda idx=i: self.on_tile_click(idx))
            btn.grid(row=i//3, column=i%3, padx=2, pady=2)
            self.buttons.append(btn)

        # Control Buttons
        self.btn_reset = tk.Button(root, text="Reset / Shuffle", font=("Helvetica", 12), bg="#2196F3", fg="white", command=self.reset_game)
        self.btn_reset.pack(pady=5, fill=tk.X, padx=50)

        self.btn_solve = tk.Button(root, text="Auto-Solve (AI)", font=("Helvetica", 12), bg="#4CAF50", fg="white", command=self.run_auto_solve)
        self.btn_solve.pack(pady=5, fill=tk.X, padx=50)

        # Start the game
        self.reset_game()

    def reset_game(self):
        """
        UPDATED: Now generates a RANDOM solvable state every time.
        It starts with the solved state and makes 50 random valid moves
        to ensure the puzzle is always solvable.
        """
        self.steps = 0
        self.update_steps_label()
        
        # 1. Start with solved state
        state = [1, 2, 3, 4, 5, 6, 7, 8, 0]
        
        # 2. Shuffle it by making random valid moves
        # We simulate 100 random moves to shuffle the board
        for _ in range(100):
            blank_index = state.index(0)
            row, col = blank_index // 3, blank_index % 3
            possible_moves = []
            
            # Check neighbors (Up, Down, Left, Right)
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = row + dr, col + dc
                if 0 <= nr < 3 and 0 <= nc < 3:
                    possible_moves.append(nr * 3 + nc)
            
            # Pick a random valid neighbor and swap
            if possible_moves:
                target = random.choice(possible_moves)
                state[blank_index], state[target] = state[target], state[blank_index]

        self.current_state = state
        self.update_board_ui()

    def update_board_ui(self):
        for i, val in enumerate(self.current_state):
            if val == 0:
                self.buttons[i].config(text="", bg="#ccc", state="disabled")
            else:
                self.buttons[i].config(text=str(val), bg="white", state="normal")

    def update_steps_label(self):
        self.label_steps.config(text=f"Steps: {self.steps}")

    def on_tile_click(self, index):
        blank_index = self.current_state.index(0)
        
        # Check if the clicked tile is adjacent to the blank space
        row, col = index // 3, index % 3
        blank_row, blank_col = blank_index // 3, blank_index % 3

        if abs(row - blank_row) + abs(col - blank_col) == 1:
            # Valid move: Swap
            self.current_state[index], self.current_state[blank_index] = self.current_state[blank_index], self.current_state[index]
            self.steps += 1
            self.update_steps_label()
            self.update_board_ui()
            
            if self.current_state == [1, 2, 3, 4, 5, 6, 7, 8, 0]:
                messagebox.showinfo("Success", f"You solved it in {self.steps} steps!")
        else:
            messagebox.showwarning("Invalid Move", "You can only move tiles adjacent to the empty space!")

    def run_auto_solve(self):
        self.btn_solve.config(state="disabled", text="Solving...")
        self.root.update()
        
        solution_path = solve_puzzle_astar(tuple(self.current_state))
        
        if solution_path is None:
            messagebox.showerror("Error", "Could not find a solution!")
        else:
            messagebox.showinfo("AI Solver", f"Solution found! Steps: {len(solution_path)}")
            # Animate the solution
            self.animate_solution(solution_path)
            
        self.btn_solve.config(state="normal", text="Auto-Solve (AI)")

    def animate_solution(self, path):
        if not path:
            return
        
        next_state = list(path.pop(0))
        self.current_state = next_state
        self.update_board_ui()
        self.root.after(500, lambda: self.animate_solution(path))

if __name__ == "__main__":
    root = tk.Tk()
    app = PuzzleGameGUI(root)
    root.mainloop()
