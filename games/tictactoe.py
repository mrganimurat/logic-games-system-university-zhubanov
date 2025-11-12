import tkinter as tk
from tkinter import messagebox
import json
import time
import threading
import os

DATA_FILE = "games/data/data.json"

class GameFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # --- Загрузка данных ---
        if not os.path.exists(DATA_FILE):
            self.data = {"x_wins": 0, "o_wins": 0, "dark_mode": False}
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4)
        else:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                self.data = json.load(f)

        self.x_wins = self.data.get("x_wins", 0)
        self.o_wins = self.data.get("o_wins", 0)
        self.dark_mode = self.data.get("dark_mode", False)
        self.board = [""] * 9
        self.current_player = "X"
        self.buttons = []

        # --- Интерфейс ---
        self.frame = tk.Frame(self)
        self.frame.pack(expand=True)

        self.score_label = tk.Label(self.frame, text=f"X: {self.x_wins}   O: {self.o_wins}", font=("Arial", 22, "bold"))
        self.score_label.grid(row=0, column=0, columnspan=3, pady=20)

        for i in range(9):
            b = tk.Button(self.frame, text="", font=("Arial", 36, "bold"), width=5, height=2,
                          command=lambda i=i: self.on_click(i))
            b.grid(row=(i // 3) + 1, column=i % 3, padx=10, pady=10)
            self.buttons.append(b)

        self.restart_button = tk.Button(self.frame, text="Қайта бастау", font=("Arial", 16), command=self.restart_game)
        self.restart_button.grid(row=5, column=0, pady=10)

        self.reset_scores_button = tk.Button(self.frame, text="Санауышты тазалау", font=("Arial", 16), command=self.reset_scores)
        self.reset_scores_button.grid(row=5, column=1, pady=10)

        self.theme_button = tk.Button(self.frame, text="Қара/Ақ режим", font=("Arial", 16), command=self.toggle_theme)
        self.theme_button.grid(row=5, column=2, pady=10)

        self.back_button = tk.Button(self.frame, text="Назад в меню", font=("Arial", 16), command=self.back_to_menu)
        self.back_button.grid(row=6, column=0, columnspan=3, pady=10)

        self.update_theme()

    # --- Логика темы ---
    def get_colors(self):
        if self.dark_mode:
            return ("#202124", "#FFFFFF", "#444444", "#00FF99")
        else:
            return ("#FFFFFF", "#000000", "#CCCCCC", "#0099FF")

    def update_theme(self):
        bg, fg, cell, accent = self.get_colors()
        self.config(bg=bg)
        self.frame.config(bg=bg)
        self.score_label.config(bg=bg, fg=fg)
        self.restart_button.config(bg=accent, fg=fg)
        self.reset_scores_button.config(bg=accent, fg=fg)
        self.theme_button.config(bg=cell, fg=fg)
        for b in self.buttons:
            b.config(bg=cell, fg=fg, activebackground=accent)

    # --- Логика игры ---
    def check_winner(self):
        wins = [
            (0,1,2), (3,4,5), (6,7,8),
            (0,3,6), (1,4,7), (2,5,8),
            (0,4,8), (2,4,6)
        ]
        for a,b,c in wins:
            if self.board[a] == self.board[b] == self.board[c] and self.board[a] != "":
                self.animate_win((a,b,c))
                if self.board[a] == "X":
                    self.x_wins += 1
                else:
                    self.o_wins += 1
                self.save_data()
                self.update_score_label()
                self.disable_all()
                return True
        if "" not in self.board:
            messagebox.showinfo("Нәтиже", "Тең ойын!")
            return True
        return False

    def animate_win(self, indices):
        bg, fg, cell, accent = self.get_colors()
        def blink():
            for _ in range(5):
                for i in indices:
                    self.buttons[i].config(bg=accent)
                time.sleep(0.25)
                for i in indices:
                    self.buttons[i].config(bg=cell)
                time.sleep(0.25)
        threading.Thread(target=blink).start()

    def on_click(self, index):
        if self.board[index] == "":
            self.board[index] = self.current_player
            self.buttons[index].config(text=self.current_player)
            if self.check_winner():
                return
            self.current_player = "O" if self.current_player == "X" else "X"

    def disable_all(self):
        for b in self.buttons:
            b.config(state="disabled")

    def restart_game(self):
        self.board = [""] * 9
        self.current_player = "X"
        for b in self.buttons:
            b.config(text="", state="normal")

    def update_score_label(self):
        self.score_label.config(text=f"X: {self.x_wins}   O: {self.o_wins}")

    def reset_scores(self):
        self.x_wins, self.o_wins = 0, 0
        self.save_data()
        self.update_score_label()

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.save_data()
        self.update_theme()

    def save_data(self):
        os.makedirs("data", exist_ok=True)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({"x_wins": self.x_wins, "o_wins": self.o_wins, "dark_mode": self.dark_mode}, f, indent=4)

    def back_to_menu(self):
        self.pack_forget()
        self.controller.back_to_menu()