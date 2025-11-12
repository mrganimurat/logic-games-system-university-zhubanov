import tkinter as tk
from games import snake, tictactoe, minesweeper

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MiniGame Center")
        self.geometry("1080x650")

        # Контейнер для всех "экранов"
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        self.frames = {}  # Словарь для хранения всех Frame

        # Инициализация главного меню
        self.frames["menu"] = self.create_menu()
        self.frames["menu"].pack(fill="both", expand=True)

    def create_menu(self):
        frame = tk.Frame(self.container)

        label = tk.Label(frame, text="Выберите игру", font=("Arial", 16))
        label.pack(pady=30)

        games_list = [
            ("Змейка", snake.GameFrame),
            ("Крестики-нолики", tictactoe.GameFrame),
            ("Сапёр", minesweeper.GameFrame)
        ]

        for name, game_class in games_list:
            btn = tk.Button(frame, text=name, font=("Arial", 14), width=20, command=lambda g=game_class: self.show_game(g))
            btn.pack(pady=10)

        btn_exit = tk.Button(frame, text="Выход", font=("Arial", 14), width=20, command=self.destroy)
        btn_exit.pack(pady=30)

        return frame

    def show_game(self, game_class):
        # Скрываем меню
        self.frames["menu"].pack_forget()

        # Если Frame ещё не создан, создаём
        if game_class not in self.frames:
            frame = game_class(self.container, self)
            self.frames[game_class] = frame
            frame.pack(fill="both", expand=True)
        else:
            self.frames[game_class].pack(fill="both", expand=True)

    def back_to_menu(self):
        # Скрываем все активные игры
        for key, frame in self.frames.items():
            if key != "menu":
                frame.pack_forget()
        self.frames["menu"].pack(fill="both", expand=True)


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()