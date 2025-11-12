# games/snake.py
import tkinter as tk
import random
import os

WIDTH = 700
HEIGHT = 400
SEG_SIZE = 25
RECORD_FILE = "games/data/record.txt"
after_id = None


class GameFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        self.controller = controller

        # Флаги и состояние
        self.after_id = None
        self.in_game = True
        self.paused = False
        self.needs_restart = False  # если True — при следующем show будет рестарт

        # Сохраняем оригинальные pack/pack_forget чтобы переопределить поведение
        self._orig_pack = self.pack
        self._orig_pack_forget = self.pack_forget
        # Переопределяем pack: если нужно — рестартим перед показом
        def _pack_wrapper(*args, **kwargs):
            if self.needs_restart:
                # Убедимся, что игра стартует "с нуля"
                self.restart_game()
                self.needs_restart = False
            return self._orig_pack(*args, **kwargs)

        # Переопределяем pack_forget: останавливаем игру и помечаем, что нужен рестарт
        def _pack_forget_wrapper(*args, **kwargs):
            # Останавливаем игровой цикл
            self.in_game = False
            # Пометим, что при следующем показе игра должна запуститься заново
            self.needs_restart = True
            return self._orig_pack_forget(*args, **kwargs)

        # Привязываем обёртки к экземпляру
        self.pack = _pack_wrapper
        self.pack_forget = _pack_forget_wrapper

        # Верхняя панель
        top = tk.Frame(self, bg="white")
        top.pack(pady=20)

        self.restart_button = tk.Button(top, text="Рестарт", bg="#d32f2f", fg="white",
                                        font=("Arial", 14), width=10, command=self.restart_game)
        self.restart_button.pack(side=tk.LEFT, padx=100)

        tk.Label(top, text="Змейка", bg="white", font=("Arial", 18)).pack(side=tk.LEFT)

        self.pause_button = tk.Button(top, text="Пауза", bg="#00cc00", fg="white",
                                      font=("Arial", 14), width=10, command=self.pause_game)
        self.pause_button.pack(side=tk.LEFT, padx=100)

        # Игровое поле
        self.canvas = tk.Canvas(self, width=WIDTH, height=HEIGHT, bg="#1e1e1e", highlightthickness=0)
        self.canvas.pack(pady=10)

        # Нижняя панель
        bottom = tk.Frame(self, bg="white")
        bottom.pack(pady=20)

        self.score_label = tk.Label(bottom, text="Счёт: 0", font=("Arial", 16), bg="white")
        self.score_label.pack(side=tk.LEFT, padx=20)

        self.record_label = tk.Label(bottom, text="Рекорд: 0", font=("Arial", 16), bg="white", fg="#0077cc")
        self.record_label.pack(side=tk.LEFT, padx=20)

        tk.Button(bottom, text="Назад в меню", bg="#4285f4", fg="white", font=("Arial", 14), width=10, command=self.back_to_menu).pack(side=tk.RIGHT, padx=20)

        # --- Инициализация ---
        self.score = self.Score(self)
        self.create_block()
        self.snake = self.create_snake()
        self.canvas.focus_set()
        self.canvas.bind("<KeyPress>", self.snake.change_direction)
        # Запускаем цикл; он сам будет управлять дальнейшими вызовами
        self.main_loop()

    # ------------------------ Вложенные классы ------------------------
    class Score:
        def __init__(self, game):
            self.game = game
            self.value = 0
            self.record = self.load_record()
            self.update_labels()

        def load_record(self):
            if os.path.exists(RECORD_FILE):
                try:
                    with open(RECORD_FILE, "r") as f:
                        return int(f.read().strip())
                except:
                    return 0
            return 0

        def save_record(self):
            os.makedirs(os.path.dirname(RECORD_FILE) or ".", exist_ok=True)
            with open(RECORD_FILE, "w") as f:
                f.write(str(self.record))

        def increment(self):
            self.value += 1
            if self.value > self.record:
                self.record = self.value
                self.save_record()
            self.update_labels()

        def reset(self):
            self.value = 0
            self.update_labels()

        def update_labels(self):
            self.game.score_label.config(text=f"Счёт: {self.value}")
            self.game.record_label.config(text=f"Рекорд: {self.record}")

    class Segment:
        def __init__(self, canvas, x, y):
            self.canvas = canvas
            self.instance = canvas.create_rectangle(
                x, y, x + SEG_SIZE, y + SEG_SIZE, fill="green", outline=""
            )

    class Snake:
        def __init__(self, game, segments):
            self.game = game
            self.canvas = game.canvas
            self.segments = segments
            self.mapping = {
                "Down": (0, 1),
                "Up": (0, -1),
                "Left": (-1, 0),
                "Right": (1, 0),
            }
            self.vector = self.mapping["Right"]

        def move(self):
            for index in range(len(self.segments) - 1):
                segment = self.segments[index].instance
                x1, y1, x2, y2 = self.canvas.coords(self.segments[index + 1].instance)
                self.canvas.coords(segment, x1, y1, x2, y2)

            x1, y1, x2, y2 = self.canvas.coords(self.segments[-2].instance)
            self.canvas.coords(
                self.segments[-1].instance,
                x1 + self.vector[0] * SEG_SIZE,
                y1 + self.vector[1] * SEG_SIZE,
                x2 + self.vector[0] * SEG_SIZE,
                y2 + self.vector[1] * SEG_SIZE,
            )

        def add_segment(self):
            self.game.score.increment()
            last_seg = self.canvas.coords(self.segments[0].instance)
            x = last_seg[2] - SEG_SIZE
            y = last_seg[3] - SEG_SIZE
            self.segments.insert(0, GameFrame.Segment(self.canvas, x, y))

        def change_direction(self, event):
            if event.keysym in self.mapping:
                opposite = {"Up": "Down", "Down": "Up", "Left": "Right", "Right": "Left"}
                if self.vector != self.mapping[opposite[event.keysym]]:
                    self.vector = self.mapping[event.keysym]

        def reset_snake(self):
            for segment in self.segments:
                self.canvas.delete(segment.instance)

    # ------------------------ Игровая логика ------------------------
    def main_loop(self):
        global IN_GAME, PAUSED, after_id
        if self.in_game:
            if not self.paused:
                self.snake.move()
                head_coords = self.canvas.coords(self.snake.segments[-1].instance)
                x1, y1, x2, y2 = head_coords

                # столкновение со стеной
                if x2 > WIDTH or x1 < 0 or y1 < 0 or y2 > HEIGHT:
                    self.game_over()
                # поедание яблока
                elif head_coords == self.canvas.coords(self.block):
                    self.snake.add_segment()
                    self.canvas.delete(self.block)
                    self.create_block()
                # столкновение с собой
                else:
                    for index in range(len(self.snake.segments) - 1):
                        if head_coords == self.canvas.coords(self.snake.segments[index].instance):
                            game_over()
                            break

            self.after_id = self.after(100, self.main_loop)
        else:
            self.canvas.create_text(WIDTH / 2, HEIGHT / 2, text="Ты проиграл!", fill="red", font=("Arial", 22))

    def game_over(self):
        # Останавливаем цикл игры — main_loop не будет запланирован дальше
        self.in_game = False

    def restart_game(self):
        global s, s, PAUSED, after_id
        # если есть активный таймер — отменяем его
        if hasattr(self, 'after_id') and self.after_id:
            self.after_cancel(self.after_id)
            self.after_id = None

        self.in_game = True
        self.paused = False
        self.pause_button.config(text="Пауза", bg="#00cc00")

        self.canvas.delete("all")
        self.score.reset()
        self.create_block()
        self.snake = self.create_snake()
        self.canvas.focus_set()
        self.canvas.bind("<KeyPress>", self.snake.change_direction)

        self.main_loop()

    def pause_game(self):
        self.paused = not self.paused
        if self.paused:
            self.pause_button.config(text="Продолжить", bg="#cccc00")
        else:
            self.pause_button.config(text="Пауза", bg="#00cc00")

    def create_snake(self):
        segments = [
            self.Segment(self.canvas, SEG_SIZE, SEG_SIZE),
            self.Segment(self.canvas, SEG_SIZE * 2, SEG_SIZE),
            self.Segment(self.canvas, SEG_SIZE * 3, SEG_SIZE),
        ]
        return self.Snake(self, segments)

    def create_block(self):
        # Создаёт яблоко; простая реализация (можно добавить проверку, чтобы не появлялось на змее)
        posx = SEG_SIZE * random.randint(1, (WIDTH - SEG_SIZE) // SEG_SIZE)
        posy = SEG_SIZE * random.randint(1, (HEIGHT - SEG_SIZE) // SEG_SIZE)
        self.block = self.canvas.create_oval(
            posx, posy, posx + SEG_SIZE, posy + SEG_SIZE, fill="red", outline=""
        )

    def back_to_menu(self):
        # Вызывается при нажатии кнопки "Назад в меню"
        # Мы используем контроллер (MainApp) — он вызовет pack_forget(), который мы переопределили
        self.controller.back_to_menu()
