import tkinter as tk
from tkinter import simpledialog, messagebox
import random
import os
import json
from datetime import datetime
from PIL import Image, ImageTk

class Tetris:
    def __init__(self, root):
        self.root = root
        self.root.title("俄罗斯方块")
        self.width = 10
        self.height = 20
        self.score = [0, 0, 0]
        self.current_tetromino = [None, None, None]
        self.cell_size = 30
        self.lines_cleared_total = [0, 0, 0]
        self.startspeed = 1000
        self.speed = [self.startspeed, self.startspeed, self.startspeed]
        self.game_over_flag = [False, False, False]
        self.paused = False
        self.shadow_enabled = [False, False, False]
        self.player_colors = ["blue", "red", "green"]
        self.player_num = None  # 记录玩家数量，None表示未选择，1表示单人，2表示双人，3表示三人
        self.game_mode = None # 记录游戏模式
        
        current_directory = os.path.dirname(os.path.abspath(__file__))
        self.cell_red_image = self.loadimage(current_directory+"\\cell_red.png")
        self.cell_cyan_image = self.loadimage(current_directory+"\\cell_cyan.png")
        self.cell_yellow_image = self.loadimage(current_directory+"\\cell_yellow.png")
        self.cell_blue_image = self.loadimage(current_directory+"\\cell_blue.png")
        self.cell_purple_image = self.loadimage(current_directory+"\\cell_purple.png")
        self.cell_green_image = self.loadimage(current_directory+"\\cell_green.png")
        self.cell_orange_image = self.loadimage(current_directory+"\\cell_orange.png")
        
        # --- 玩家1 ---
        self.canvas1 = tk.Canvas(root, width=self.width * self.cell_size, height=self.height * self.cell_size, bg="grey")
        self.canvas1.grid(row=0, column=0, rowspan=20)
        self.next_canvas1 = tk.Canvas(root, width=4 * self.cell_size, height=4 * self.cell_size)
        self.next_canvas1.grid(row=0, column=1)
        self.score_label1 = tk.Label(root, text="玩家1分数: 0", font=("Arial", 16))
        self.score_label1.grid(row=1, column=1)

        # --- 玩家2 ---
        self.canvas2 = tk.Canvas(root, width=self.width * self.cell_size, height=self.height * self.cell_size, bg="grey")
        self.canvas2.grid(row=0, column=2, rowspan=20)
        self.next_canvas2 = tk.Canvas(root, width=4 * self.cell_size, height=4 * self.cell_size)
        self.next_canvas2.grid(row=0, column=3)
        self.score_label2 = tk.Label(root, text="玩家2分数: 0", font=("Arial", 16))
        self.score_label2.grid(row=1, column=3)

        # --- 玩家3 ---
        self.canvas3 = tk.Canvas(root, width=self.width * self.cell_size, height=self.height * self.cell_size, bg="grey")
        self.canvas3.grid(row=0, column=4, rowspan=20)
        self.next_canvas3 = tk.Canvas(root, width=4 * self.cell_size, height=4 * self.cell_size)
        self.next_canvas3.grid(row=0, column=5)
        self.next_canvas3.grid_remove() #初始隐藏
        self.score_label3 = tk.Label(root, text="玩家3分数: 0", font=("Arial", 16))
        self.score_label3.grid(row=1, column=5)

        #抢方块模式的next_canvas
        self.next_canvas = tk.Canvas(root, width=4 * self.cell_size, height=4 * self.cell_size)
        self.next_canvas.grid(row=0, column=5)
        self.next_canvas.grid_remove() #初始隐藏

        # ---  其他UI ---
        self.high_score_label = tk.Label(root, text="最高分: 0", font=("Arial", 16))
        self.high_score_label.grid(row=2, column=5, columnspan=2)

        self.rank_listbox = tk.Listbox(root, height=13, font=("Arial", 12), width=25)
        self.rank_listbox.grid(row=3, column=5, rowspan=15, columnspan=2)

        self.choose_mode_button = tk.Button(root, text="选择模式", font=("Arial", 16), command=self.choose_game_mode, width=15)
        self.choose_mode_button.grid(row=19, column=5, columnspan=2)

        self.start_button = tk.Button(root, text="开始游戏", font=("Arial", 16), command=self.start_game, width=15)
        self.start_button.grid(row=20, column=5, columnspan=2)
        self.start_button.grid_remove() #初始隐藏

        self.high_scores = Tetris.load_high_scores()
        self.update_high_score_label()
        self.update_rank_listbox()

        self.root.bind("<Key>", self.handle_keypress)
        self.paused_by_focus = False
        self.root.bind("<FocusOut>", self.pause_game_focus_out)
        self.root.bind("<FocusIn>", self.resume_game_focus_in)
        Tetris.center_window(root)

        for i in range(3):
            canvas = self.canvas1 if i == 0 else (self.canvas2 if i == 1 else self.canvas3)
            canvas.create_rectangle(0, 0, self.width * self.cell_size, self.height * self.cell_size, fill=None, outline="black")

    def loadimage(self,filepath):
        try:
            image = Image.open(filepath)
            image = image.resize((self.cell_size, self.cell_size)) # , Image.ANTIALIAS
            return ImageTk.PhotoImage(image)
        except Exception as e:
            print(f"Error loading and resizing image: {e}")
            return None


    @staticmethod
    def center_window(window):
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        window.geometry(f"+{x}+{y}")

    @staticmethod
    def load_high_scores():
        if os.path.exists("highscores.json"):
            with open("highscores.json", "r") as f:
                return json.load(f)
        return []
    
    def choose_game_mode(self):
        def on_mode_select():
            self.player_num = player_num_var.get()
            self.game_mode = game_mode_var.get()
            mode_window.destroy()
            self.start_button.grid()
            self.choose_mode_button.grid_remove()

            if self.player_num == 1:  # 单人模式
                self.canvas2.grid_remove()
                self.score_label2.grid_remove()
                self.next_canvas2.grid_remove()
                self.canvas3.grid_remove()
                self.score_label3.grid_remove()
                self.next_canvas3.grid_remove()
                if self.game_mode == 1:
                    self.next_canvas1.grid_remove()
                    # 抢方块模式的next_canvas
                    self.next_canvas.grid(row=0, column=1)
                else:
                    self.next_canvas1.grid()
                    self.next_canvas.grid_remove()

            elif self.player_num == 2: #双人模式
                self.canvas2.grid()
                self.score_label2.grid()
                self.canvas3.grid_remove()
                self.score_label3.grid_remove()
                self.next_canvas3.grid_remove()
                if self.game_mode == 1:
                    self.next_canvas1.grid_remove()
                    self.next_canvas2.grid_remove()
                    # 抢方块模式的next_canvas
                    self.next_canvas.grid(row=0, column=3)
                else:
                    self.next_canvas1.grid()
                    self.next_canvas2.grid()
                    self.next_canvas.grid_remove()

            else: #三人模式
                self.canvas2.grid()
                self.score_label2.grid()
                self.next_canvas2.grid()
                self.canvas3.grid()
                self.score_label3.grid()
                if self.game_mode == 1:
                    self.next_canvas1.grid_remove()
                    self.next_canvas2.grid_remove()
                    self.next_canvas3.grid_remove()
                    # 抢方块模式的next_canvas
                    # 此处明确设置显示位置 
                    self.next_canvas.grid(row=0, column=5)
                else:
                    self.next_canvas1.grid()
                    self.next_canvas2.grid()
                    self.next_canvas3.grid()
                    self.next_canvas.grid_remove()
                    
        mode_window = tk.Toplevel(self.root)
        mode_window.title("选择游戏模式")
        
        player_num_var = tk.IntVar(value=3)
        game_mode_var = tk.IntVar(value=0)
        Tetris.center_window(mode_window)

        tk.Label(mode_window, text="选择玩家数量:").pack()
        tk.Radiobutton(mode_window, text="单人模式", variable=player_num_var, value=1).pack()
        tk.Radiobutton(mode_window, text="双人模式", variable=player_num_var, value=2).pack()
        tk.Radiobutton(mode_window, text="三人模式", variable=player_num_var, value=3).pack()
        tk.Label(mode_window, text="选择游戏模式:").pack()
        tk.Radiobutton(mode_window, text="正常模式", variable=game_mode_var, value=0).pack()
        tk.Radiobutton(mode_window, text="抢方块模式", variable=game_mode_var, value=1).pack()
        tk.Button(mode_window, text="确定", command=on_mode_select).pack()
    
    def start_game(self):
        if self.player_num is None:
            messagebox.showinfo("提示", "请先选择游戏模式！")
            return
        player1_score_str = "玩家1分数: 0"
        player2_score_str = "玩家2分数: 0"
        player3_score_str = "玩家3分数: 0"
        if self.player_num == 1:
            self.score = [0]
            self.board = [[[0 for _ in range(self.width)] for _ in range(self.height)] for _ in range(1)]
            self.current_tetromino = [None]
            self.game_over_flag = [False]
            self.lines_cleared_total = [0]
            self.speed = [self.startspeed]
            if self.game_mode == 0:
                self.next_tetromino = [self.new_tetromino()]
            else:
                self.next_tetromino = self.new_tetromino()
            self.spawn_tetromino(0)
            self.score_label1.config(text=player1_score_str)

        elif self.player_num == 2:
            self.score = [0, 0]
            self.board = [[[0 for _ in range(self.width)] for _ in range(self.height)] for _ in range(2)]
            self.current_tetromino = [None, None]
            self.game_over_flag = [False, False]
            self.lines_cleared_total = [0, 0]
            self.speed = [self.startspeed, self.startspeed]
            if self.game_mode == 0:
                self.next_tetromino = [self.new_tetromino(), self.new_tetromino()]
            else:
                self.next_tetromino = self.new_tetromino()
            self.spawn_tetromino(0)
            self.spawn_tetromino(1)
            self.score_label1.config(text=player1_score_str)
            self.score_label2.config(text=player2_score_str)

        else:
            self.score = [0, 0, 0]
            self.board = [[[0 for _ in range(self.width)] for _ in range(self.height)] for _ in range(3)]
            self.current_tetromino = [None, None, None]
            self.game_over_flag = [False, False, False]
            if self.game_mode == 0:
                self.next_tetromino = [self.new_tetromino(), self.new_tetromino(), self.new_tetromino()]
            else:
                self.next_tetromino = self.new_tetromino()
            self.spawn_tetromino(0)
            self.spawn_tetromino(1)
            self.spawn_tetromino(2)
            self.score_label1.config(text=player1_score_str)
            self.score_label2.config(text=player2_score_str)
            self.score_label3.config(text=player3_score_str)
            self.lines_cleared_total = [0, 0, 0]
            self.speed = [self.startspeed, self.startspeed, self.startspeed]

        self.update_canvas()
        self.update_next_canvas()
        self.root.after(self.speed[0], self.game_tick)
        self.start_button.grid_remove()

    def new_tetromino(self):
        shapes = [
            {"shape": [[1, 1, 1, 1]], "color": "cyan"},  # I
            {"shape": [[1, 1], [1, 1]], "color": "yellow"},  # O
            {"shape": [[1, 1, 1], [0, 1, 0]], "color": "purple"},  # T
            {"shape": [[1, 1, 0], [0, 1, 1]], "color": "green"},  # S
            {"shape": [[0, 1, 1], [1, 1, 0]], "color": "red"},  # Z
            {"shape": [[1, 1, 1], [1, 0, 0]], "color": "orange"},  # L
            {"shape": [[1, 1, 1], [0, 0, 1]], "color": "blue"},  # J
        ]
        tetromino = random.choice(shapes)
        return {'shape': tetromino['shape'], 'color': tetromino['color'], 'x': self.width // 2 - len(tetromino['shape'][0]) // 2, 'y': 0}


    def spawn_tetromino(self, player):
        if self.game_mode == 0:
            self.current_tetromino[player] = self.next_tetromino[player]
            self.next_tetromino[player] = self.new_tetromino()
        else:
            if self.current_tetromino[player] is None:
                self.current_tetromino[player] = self.new_tetromino()
            else:
                self.current_tetromino[player] = self.next_tetromino
                self.next_tetromino = self.new_tetromino()
        if not self.is_valid_position(self.current_tetromino[player], player):
            self.game_over(player)
        self.update_next_canvas()

    def is_valid_position(self, tetromino, player, dx=0, dy=0):
        for y, row in enumerate(tetromino['shape']):
            for x, cell in enumerate(row):
                if cell:
                    new_x = tetromino['x'] + x + dx
                    new_y = tetromino['y'] + y + dy
                    if new_x < 0 or new_x >= self.width or new_y >= self.height:
                        return False
                    if new_y >= 0 and self.board[player][new_y][new_x]:
                        return False
        return True

    def place_tetromino(self, player):
        for y, row in enumerate(self.current_tetromino[player]['shape']):
            for x, cell in enumerate(row):
                if cell:
                    self.board[player][self.current_tetromino[player]['y'] + y][self.current_tetromino[player]['x'] + x] = self.current_tetromino[player]['color']
        self.clear_lines(player)
        self.spawn_tetromino(player)

    def clear_lines(self, player):
        new_board = [row for row in self.board[player] if not all(row)]
        lines_cleared = self.height - len(new_board)
        self.score[player] += lines_cleared * 10
        
        if player == 0:
            self.score_label1.config(text=f"玩家1分数: {self.score[player]}")
        elif player == 1:
            self.score_label2.config(text=f"玩家2分数: {self.score[player]}")
        else:
            self.score_label3.config(text=f"玩家3分数: {self.score[player]}")
        
        new_board = [[0] * self.width for _ in range(lines_cleared)] + new_board
        self.board[player] = new_board
        
        self.lines_cleared_total[player] += lines_cleared

        if self.lines_cleared_total[player] >= 50:
            self.lines_cleared_total[player] -= 50
            self.speed[player] = max(50, self.speed[player] - 100)

    def rotate_tetromino(self, player):
        rotated_shape = list(zip(*self.current_tetromino[player]['shape'][::-1]))
        rotated_tetromino = {'shape': rotated_shape, 'color': self.current_tetromino[player]['color'], 'x': self.current_tetromino[player]['x'], 'y': self.current_tetromino[player]['y']}
        if self.is_valid_position(rotated_tetromino, player):
            self.current_tetromino[player] = rotated_tetromino

    def move_tetromino(self, player, dx, dy):
        if self.is_valid_position(self.current_tetromino[player], player, dx, dy):
            self.current_tetromino[player]['x'] += dx
            self.current_tetromino[player]['y'] += dy
        elif dy > 0:
            self.place_tetromino(player)

    def game_tick(self):
        if not self.paused:
            for i in range(self.player_num):
                if not self.game_over_flag[i]:
                    self.move_tetromino(i, 0, 1)
            self.update_canvas()
        if not all(self.game_over_flag):
            self.root.after(min(self.speed), self.game_tick)

    def update_canvas(self):
        canvases = [self.canvas1, self.canvas2, self.canvas3]
        if self.player_num is not None:
            for player in range(self.player_num):
                canvas = canvases[player]
                canvas.delete("all")
                if hasattr(self,'board'):
                    for y, row in enumerate(self.board[player]):
                        for x, cell in enumerate(row):
                            if cell:
                                self.draw_cell(canvas, x, y, cell)
                if self.shadow_enabled[player]:
                    shadow_tetromino = self.get_shadow_tetromino(player)
                    for y, row in enumerate(shadow_tetromino['shape']):
                        for x, cell in enumerate(row):
                            if cell:
                                self.draw_cell(canvas, shadow_tetromino['x'] + x, shadow_tetromino['y'] + y, "lightgrey")
                if hasattr(self,'current_tetromino'):
                    if self.current_tetromino[player]:
                        for y, row in enumerate(self.current_tetromino[player]['shape']):
                            for x, cell in enumerate(row):
                                if cell:
                                    self.draw_cell(canvas, self.current_tetromino[player]['x'] + x, self.current_tetromino[player]['y'] + y, self.current_tetromino[player]['color'])

    def update_next_canvas(self):
        if self.game_mode == 0:
            canvases = [self.next_canvas1, self.next_canvas2, self.next_canvas3]
            for i in range(self.player_num):
                canvases[i].delete("all")
                for y, row in enumerate(self.next_tetromino[i]['shape']):
                    for x, cell in enumerate(row):
                        if cell:
                           self.draw_cell(canvases[i], x, y, self.next_tetromino[i]['color'])
        else:
            self.next_canvas.delete("all")
            for y, row in enumerate(self.next_tetromino['shape']):
                for x, cell in enumerate(row):
                    if cell:
                        self.draw_cell(self.next_canvas, x, y, self.next_tetromino['color'])

        
    def draw_cell(self, canvas, x, y, color):
        x1 = x * self.cell_size
        y1 = y * self.cell_size
        x2 = x1 + self.cell_size
        y2 = y1 + self.cell_size
        
        if color == "red" and self.cell_red_image:
            canvas.create_image(x1, y1, anchor=tk.NW, image=self.cell_red_image)
        elif color == "cyan" and self.cell_cyan_image:
            canvas.create_image(x1, y1, anchor=tk.NW, image=self.cell_cyan_image)
        elif color == "yellow" and self.cell_yellow_image:
            canvas.create_image(x1, y1, anchor=tk.NW, image=self.cell_yellow_image)
        elif color == "blue" and self.cell_blue_image:
            canvas.create_image(x1, y1, anchor=tk.NW, image=self.cell_blue_image)
        elif color == "green" and self.cell_green_image:
            canvas.create_image(x1, y1, anchor=tk.NW, image=self.cell_green_image)
        elif color == "purple" and self.cell_purple_image:
            canvas.create_image(x1, y1, anchor=tk.NW, image=self.cell_purple_image)
        elif color == "orange" and self.cell_orange_image:
            canvas.create_image(x1, y1, anchor=tk.NW, image=self.cell_orange_image)
        else:
            canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")

    def get_shadow_tetromino(self, player):
            shadow = {'shape': self.current_tetromino[player]['shape'], 'color': self.current_tetromino[player]['color'], 'x': self.current_tetromino[player]['x'], 'y': self.current_tetromino[player]['y']}
            while self.is_valid_position(shadow, player, dy=1):
                shadow['y'] += 1
            return shadow

    def drop_tetromino(self, player):
        while self.is_valid_position(self.current_tetromino[player], player, dy=1):
            self.current_tetromino[player]['y'] += 1
        self.place_tetromino(player)
        self.update_canvas()

    def pause_game_focus_out(self, event=None):
        if not self.paused and not all(self.game_over_flag):
            self.paused = True
            self.paused_by_focus = True
            self.canvas1.create_text(self.width * self.cell_size // 2, self.height * self.cell_size // 2,
                                        text="暂停", fill="green", font=("Arial", 24))
            self.canvas2.create_text(self.width * self.cell_size // 2, self.height * self.cell_size // 2,
                                        text="暂停", fill="green", font=("Arial", 24))
            self.canvas3.create_text(self.width * self.cell_size // 2, self.height * self.cell_size // 2,
                                    text="暂停", fill="green", font=("Arial", 24))


    def resume_game_focus_in(self, event=None):
        if self.paused and self.paused_by_focus:
            self.paused = False
            self.paused_by_focus = False
            self.update_canvas()
    
    def handle_keypress(self, event):
        if event.keysym == "p" or event.keysym == "P":
            if not all(self.game_over_flag):
                self.paused = not self.paused
                if self.paused:
                    self.canvas1.create_text(self.width * self.cell_size // 2, self.height * self.cell_size // 2,
                                            text="暂停", fill="green", font=("Arial", 24))
                    self.canvas2.create_text(self.width * self.cell_size // 2, self.height * self.cell_size // 2,
                                            text="暂停", fill="green", font=("Arial", 24))
                    self.canvas3.create_text(self.width * self.cell_size // 2, self.height * self.cell_size // 2,
                                        text="暂停", fill="green", font=("Arial", 24))
                else:
                    self.update_canvas()
        elif not self.paused:
            if event.keysym == "a" or event.keysym == "A": 
                self.move_tetromino(0, -1, 0)
            elif event.keysym == "d" or event.keysym == "D":
                self.move_tetromino(0, 1, 0)
            #elif event.keysym == "s":
            #    self.move_tetromino(0, 0, 1)
            elif event.keysym == "w" or event.keysym == "W":
                self.rotate_tetromino(0)
            elif event.keysym == "s" or event.keysym == "S":
                self.drop_tetromino(0)
            elif event.keysym == "Left":
                if self.player_num==3:
                    self.move_tetromino(2, -1, 0)
            elif event.keysym == "Right":
                if self.player_num==3:
                    self.move_tetromino(2, 1, 0)
            elif event.keysym == "Down": 
                if self.player_num==3:
                    self.drop_tetromino(2)
            elif event.keysym == "Up":
                if self.player_num==3:
                    self.rotate_tetromino(2)
            elif event.keysym == "j" or event.keysym == "J":
                if self.player_num>=2:
                    self.move_tetromino(1, -1, 0)
            elif event.keysym == "l" or event.keysym == "L":
                if self.player_num>=2:
                    self.move_tetromino(1, 1, 0)
            elif event.keysym == "i" or event.keysym == "I":
                if self.player_num>=2:
                    self.rotate_tetromino(1)
            elif event.keysym == "k" or event.keysym == "K":
                if self.player_num>=2:
                    self.drop_tetromino(1)
            elif event.keysym == "1":
                self.shadow_enabled[0] = not self.shadow_enabled[0]
            elif event.keysym == "2":
                self.shadow_enabled[1] = not self.shadow_enabled[1]
            elif event.keysym == "3":
                self.shadow_enabled[2] = not self.shadow_enabled[2]
            self.update_canvas()


    def game_over(self, player):
        self.game_over_flag[player] = True;
        if player == 0:
            canvas = self.canvas1
        elif player == 1:
            canvas = self.canvas2
        else :
            canvas = self.canvas3
        canvas.create_text(self.width * self.cell_size // 2, self.height * self.cell_size // 2,
                           text="游戏结束", fill="red", font=("Arial", 24))
        if all(self.game_over_flag):
            player_name = simpledialog.askstring("输入名称", "请输入胜利玩家名称:")
            if not player_name:
                player_name = "匿名玩家"
            winning_score = max(self.score)

            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_entry = {"name": player_name, "score": winning_score, "date": current_time}
            self.high_scores.append(new_entry)
            self.high_scores = sorted(self.high_scores, key=lambda x: x["score"], reverse=True)[:10000]
            self.save_high_scores()
            self.update_high_score_label()
            self.update_rank_listbox()
            self.start_button.grid()
            self.choose_mode_button.grid()
            self.game_mode = None

    def save_high_scores(self):
        with os.fdopen(os.open("highscores.json", os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644), "w") as f:
            json.dump(self.high_scores, f, indent=4)

    def update_high_score_label(self):
        if self.high_scores:
            highest_score = self.high_scores[0]["score"]
            self.high_score_label.config(text=f"最高分: {highest_score}")
        else:
            self.high_score_label.config(text="最高分: 0")

    def update_rank_listbox(self):
        self.rank_listbox.delete(0, tk.END)
        for entry in self.high_scores:
            score_text = f"{entry['name']} - {entry['score']} - {entry['date']}"
            self.rank_listbox.insert(tk.END, score_text)




if __name__ == "__main__":
    root = tk.Tk()
    game = Tetris(root)
    root.mainloop()
