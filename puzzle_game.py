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
        self.root.geometry("600x650") # Slightly taller for the label
        
        # Colors based on reference image
        self.COLOR_BG = "#2962FF"       # Bright Blue background
        self.COLOR_BOARD = "#8D6E63"    # Medium Wood for board frame
        self.COLOR_TILE = "#A1887F"     # Light Wood for tiles
        self.COLOR_TEXT = "#3E2723"     # Dark Brown for text
        self.COLOR_BTN_BG = "#0D1117"   # Dark/Black for buttons
        self.COLOR_BTN_FG = "#FFFFFF"   # White text for buttons

        self.root.configure(bg=self.COLOR_BG)

        self.steps = 0
        self.current_state = []
        
        # Main Layout Container to center everything
        self.main_container = tk.Frame(root, bg=self.COLOR_BG)
        self.main_container.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

        # 0. Steps Label (New)
        self.label_steps = tk.Label(self.main_container, text="Steps: 0", font=("Helvetica", 24, "bold"), 
                                    bg=self.COLOR_BG, fg="white")
        self.label_steps.pack(pady=(0, 10))

        # 1. Game Board Area (The "Wooden Box")
        # Using a frame with padding to simulate the box edge
        self.frame_board_outer = tk.Frame(self.main_container, bg=self.COLOR_BOARD, padx=10, pady=10, relief="raised", bd=5)
        self.frame_board_outer.pack(pady=(10, 30)) # More padding at bottom to separate from buttons

        self.buttons = []
        self.tile_frames = {} # Store frames to maybe add fancy borders if needed

        # Create 3x3 Grid
        for i in range(9):
            # Each tile is a button
            btn = tk.Button(self.frame_board_outer, text="", font=("Helvetica", 36, "bold"), 
                            width=3, height=1, # Initial size, adjusted by font
                            bg=self.COLOR_TILE, fg=self.COLOR_TEXT,
                            relief="raised", bd=5, # 3D look
                            activebackground="#D7CCC8",
                            command=lambda idx=i: self.on_tile_click(idx))
            
            # Grid placement
            btn.grid(row=i//3, column=i%3, padx=2, pady=2)
            self.buttons.append(btn)

        # 2. Control Buttons Area
        self.frame_controls = tk.Frame(self.main_container, bg=self.COLOR_BG)
        self.frame_controls.pack(fill=tk.X, pady=10)

        # Button Style
        btn_style = {"font": ("Arial", 10), "bg": self.COLOR_BTN_BG, "fg": self.COLOR_BTN_FG, 
                     "relief": "flat", "padx": 10, "pady": 5, "width": 12}

        # Row of 3 buttons (Removed Next Image)
        # 1. Randomize
        self.btn_random = tk.Button(self.frame_controls, text="Randomize", command=self.reset_game, **btn_style)
        self.btn_random.pack(side=tk.LEFT, padx=5, expand=True)

        # 2. Reset 
        self.btn_reset = tk.Button(self.frame_controls, text="Reset", command=self.reset_to_solved, **btn_style)
        self.btn_reset.pack(side=tk.LEFT, padx=5, expand=True)

        # 3. Solve Using A*
        self.btn_solve = tk.Button(self.frame_controls, text="Solve Using A*", command=self.run_auto_solve, **btn_style)
        self.btn_solve.pack(side=tk.LEFT, padx=5, expand=True)

        # Start game
        self.reset_game()

    def update_steps_label(self):
        self.label_steps.config(text=f"Steps: {self.steps}")

    def reset_game(self):
        """Shuffle board to a random solvable state."""
        self.steps = 0
        self.update_steps_label()
        state = [1, 2, 3, 4, 5, 6, 7, 8, 0]
        # Shuffle
        for _ in range(100):
            blank_index = state.index(0)
            row, col = blank_index // 3, blank_index % 3
            possible_moves = []
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = row + dr, col + dc
                if 0 <= nr < 3 and 0 <= nc < 3:
                    possible_moves.append(nr * 3 + nc)
            if possible_moves:
                target = random.choice(possible_moves)
                state[blank_index], state[target] = state[target], state[blank_index]
        self.current_state = state
        self.update_board_ui()

    def reset_to_solved(self):
        """Reset immediately to the solved state."""
        self.current_state = [1, 2, 3, 4, 5, 6, 7, 8, 0]
        self.steps = 0
        self.update_steps_label()
        self.update_board_ui()

    def update_board_ui(self):
        for i, val in enumerate(self.current_state):
            if val == 0:
                # Empty tile - show background of the board to simulate hole
                self.buttons[i].config(text="", bg=self.COLOR_BOARD, state="disabled", relief="flat")
            else:
                self.buttons[i].config(text=str(val), bg=self.COLOR_TILE, fg=self.COLOR_TEXT, 
                                       state="normal", relief="raised")

    def on_tile_click(self, index):
        if self.btn_solve.cget("state") == "disabled": return # Block clicks while solving

        blank_index = self.current_state.index(0)
        row, col = index // 3, index % 3
        blank_row, blank_col = blank_index // 3, blank_index % 3

        if abs(row - blank_row) + abs(col - blank_col) == 1:
            self.current_state[index], self.current_state[blank_index] = self.current_state[blank_index], self.current_state[index]
            self.steps += 1
            self.update_steps_label()
            self.update_board_ui()
            
            if self.current_state == [1, 2, 3, 4, 5, 6, 7, 8, 0]:
                messagebox.showinfo("Success", f"You solved it in {self.steps} steps!")

    def run_auto_solve(self):
        self.btn_solve.config(state="disabled", text="Solving...")
        self.root.update()
        
        solution_path = solve_puzzle_astar(tuple(self.current_state))
        
        if solution_path is None:
            messagebox.showerror("Error", "Could not find a solution!")
            self.btn_solve.config(state="normal", text="Solve Using A*")
        else:
            # Don't reset steps here, let it count up as it solves, or reset to 0 to show solution length?
            # User asked "count the step to know the user and the AI with how many step can solve it"
            # It usually implies showing the count of the *solution*. 
            # So let's reset to 0 before animating so it shows the AI's step count.
            self.steps = 0 
            self.update_steps_label()
            
            # messagebox.showinfo("AI Solver", f"Solution found! Steps: {len(solution_path)}") # Can be annoying if we want to watch
            self.animate_solution(solution_path)
            
    def animate_solution(self, path):
        if not path:
            self.btn_solve.config(state="normal", text="Solve Using A*")
            if self.current_state == [1, 2, 3, 4, 5, 6, 7, 8, 0]:
                 messagebox.showinfo("AI Solver", f"AI Solved it in {self.steps} steps!")
            return
        
        next_state = list(path.pop(0))
        self.current_state = next_state
        self.steps += 1
        self.update_steps_label()
        self.update_board_ui()
        self.root.after(300, lambda: self.animate_solution(path))

if __name__ == "__main__":
    root = tk.Tk()
    app = PuzzleGameGUI(root)
    root.mainloop()
