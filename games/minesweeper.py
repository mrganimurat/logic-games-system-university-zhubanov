import tkinter as tk
from tkinter import messagebox
import random, json, os

SAVE_FILE = "games/data/mina_save.json"
NUMBER_COLORS = {1:"blue", 2:"green", 3:"red", 4:"purple", 5:"maroon", 6:"turquoise", 7:"black", 8:"gray"}

class GameFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.config(bg="#e8f0f7")

        # --- Верхняя панель ---
        self.frame_top = tk.Frame(self, bg="#e8f0f7")
        self.frame_top.pack(pady=15)

        tk.Label(self.frame_top, text="Қатар:", font=("Arial", 11, "bold"), bg="#e8f0f7").grid(row=0, column=0, padx=5)
        self.rows_entry = tk.Entry(self.frame_top, width=5)
        self.rows_entry.insert(0, "5")
        self.rows_entry.grid(row=0, column=1, padx=5)

        tk.Label(self.frame_top, text="Баған:", font=("Arial", 11, "bold"), bg="#e8f0f7").grid(row=0, column=2, padx=5)
        self.cols_entry = tk.Entry(self.frame_top, width=5)
        self.cols_entry.insert(0, "5")
        self.cols_entry.grid(row=0, column=3, padx=5)

        tk.Label(self.frame_top, text="Мина саны:", font=("Arial", 11, "bold"), bg="#e8f0f7").grid(row=0, column=4, padx=5)
        self.mines_entry = tk.Entry(self.frame_top, width=5)
        self.mines_entry.insert(0, "5")
        self.mines_entry.grid(row=0, column=5, padx=5)

        self.start_button = tk.Button(self.frame_top, text="▶️ Бастау", bg="#4CAF50", fg="white",
                                      font=("Arial", 11, "bold"), command=self.new_game)
        self.start_button.grid(row=0, column=6, padx=10)

        self.reset_button = tk.Button(self.frame_top, text="🔄 Қайта бастау", bg="#2196F3", fg="white",
                                      font=("Arial", 11, "bold"), command=self.reset_game)
        self.reset_button.grid(row=0, column=7, padx=10)

        self.back_button = tk.Button(self.frame_top, text="Назад в меню", bg="#d32f2f", fg="white",
                                     font=("Arial", 11, "bold"), command=self.back_to_menu)
        self.back_button.grid(row=0, column=8, padx=10)

        # --- Игровое поле ---
        self.frame_board = tk.Frame(self, bg="#e8f0f7")
        self.frame_board.pack(pady=20)

        # --- Данные ---
        self.buttons = {}
        self.mines = set()
        self.opened = set()
        self.flags = set()
        self.rows = 0
        self.cols = 0
        self.mine_count = 0

        if os.path.exists(SAVE_FILE):
            self.load_game()

    # --- Игровая логика ---
    def new_game(self):
        try:
            self.rows = int(self.rows_entry.get())
            self.cols = int(self.cols_entry.get())
            self.mine_count = int(self.mines_entry.get())
            if self.rows <= 0 or self.cols <= 0 or self.mine_count <= 0:
                raise ValueError
            if self.mine_count >= self.rows * self.cols:
                messagebox.showerror("Қате!", "Мина саны ұяшық санынан аз болуы керек!")
                return
        except ValueError:
            messagebox.showerror("Қате!", "Дұрыс мәндер енгізіңіз!")
            return

        self.mines.clear()
        self.opened.clear()
        self.flags.clear()

        for widget in self.frame_board.winfo_children():
            widget.destroy()
        self.buttons.clear()

        for r in range(self.rows):
            for c in range(self.cols):
                btn = tk.Button(
                    self.frame_board, text="", width=4, height=2,
                    bg="#cce7ff", relief="raised", font=("Arial", 12, "bold"),
                    command=lambda r=r, c=c: self.open_cell(r, c)
                )
                btn.bind("<Button-3>", lambda e, r=r, c=c: self.toggle_flag(r, c))
                btn.grid(row=r, column=c, padx=1, pady=1)
                self.buttons[(r, c)] = btn

        while len(self.mines) < self.mine_count:
            self.mines.add((random.randint(0, self.rows - 1), random.randint(0, self.cols - 1)))

        self.save_game()

    def reset_game(self):
        if os.path.exists(SAVE_FILE):
            os.remove(SAVE_FILE)
        self.new_game()

    def count_mines_around(self, r, c):
        return sum(
            (i, j) in self.mines
            for i in range(r - 1, r + 2)
            for j in range(c - 1, c + 2)
            if 0 <= i < self.rows and 0 <= j < self.cols
        )

    def open_cell(self, r, c):
        if (r, c) in self.opened or (r, c) in self.flags:
            return

        btn = self.buttons[(r, c)]
        if (r, c) in self.mines:
            btn.config(text="💣", bg="#ff4c4c", fg="white")
            self.reveal_all()
            messagebox.showinfo("Ойын бітті!", "Келесі ойынға сәттілік!")
            if os.path.exists(SAVE_FILE):
                os.remove(SAVE_FILE)
            return

        self.opened.add((r, c))
        count = self.count_mines_around(r, c)
        color = NUMBER_COLORS.get(count, "black")
        btn.config(text=str(count) if count else "", bg="#dfe6e9", fg=color, relief="sunken", state="disabled")

        if count == 0:
            for i in range(r - 1, r + 2):
                for j in range(c - 1, c + 2):
                    if 0 <= i < self.rows and 0 <= j < self.cols:
                        self.open_cell(i, j)

        self.check_win()
        self.save_game()

    def toggle_flag(self, r, c):
        if (r, c) in self.opened:
            return
        btn = self.buttons[(r, c)]
        if (r, c) in self.flags:
            self.flags.remove((r, c))
            btn.config(text="", bg="#cce7ff")
        else:
            self.flags.add((r, c))
            btn.config(text="🚩", bg="#f0d14c")
        self.save_game()

    def check_win(self):
        if len(self.opened) + len(self.mines) == self.rows * self.cols:
            self.reveal_all()
            messagebox.showinfo("🎉 Жеңіс!", "Барлық минаны таптыңыз!")
            if os.path.exists(SAVE_FILE):
                os.remove(SAVE_FILE)

    def reveal_all(self):
        for (r, c), btn in self.buttons.items():
            if (r, c) in self.mines:
                btn.config(text="💣", bg="#ff7675", fg="white")
            elif (r, c) not in self.opened:
                count = self.count_mines_around(r, c)
                color = NUMBER_COLORS.get(count, "black")
                btn.config(text=str(count) if count else "", bg="#dfe6e9", fg=color)

    def save_game(self):
        if not self.rows or not self.cols:
            return
        state = {
            "rows": self.rows,
            "cols": self.cols,
            "mine_count": self.mine_count,
            "mines": list(self.mines),
            "opened": list(self.opened),
            "flags": list(self.flags),
        }
        os.makedirs("games/data", exist_ok=True)
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f)

    def load_game(self):
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.rows = data["rows"]
        self.cols = data["cols"]
        self.mine_count = data["mine_count"]
        self.mines = set(tuple(x) for x in data["mines"])
        self.opened = set(tuple(x) for x in data["opened"])
        self.flags = set(tuple(x) for x in data["flags"])

        self.rows_entry.delete(0, tk.END)
        self.rows_entry.insert(0, str(self.rows))
        self.cols_entry.delete(0, tk.END)
        self.cols_entry.insert(0, str(self.cols))
        self.mines_entry.delete(0, tk.END)
        self.mines_entry.insert(0, str(self.mine_count))

        for widget in self.frame_board.winfo_children():
            widget.destroy()
        self.buttons.clear()

        for r in range(self.rows):
            for c in range(self.cols):
                btn = tk.Button(
                    self.frame_board, text="", width=4, height=2,
                    bg="#cce7ff", relief="raised", font=("Arial", 12, "bold"),
                    command=lambda r=r, c=c: self.open_cell(r, c)
                )
                btn.bind("<Button-3>", lambda e, r=r, c=c: self.toggle_flag(r, c))
                btn.grid(row=r, column=c, padx=1, pady=1)
                self.buttons[(r, c)] = btn

        for (r, c) in self.opened:
            count = self.count_mines_around(r, c)
            color = NUMBER_COLORS.get(count, "black")
            self.buttons[(r, c)].config(
                text=str(count) if count else "", bg="#dfe6e9", fg=color, relief="sunken", state="disabled"
            )
        for (r, c) in self.flags:
            self.buttons[(r, c)].config(text="🚩", bg="#f0d14c")

    def back_to_menu(self):
        self.pack_forget()
        self.controller.back_to_menu()
