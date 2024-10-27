# -*- coding: utf-8 -*-
# https://github.com/epicblue/tetris
# epicblue@qq.com 2024

import tkinter as tk
from tkinter import simpledialog, messagebox
import random
import os
import json
from datetime import datetime

class Tetris:
    def __init__(self, root):
        self.root = root
        self.root.title("三人俄罗斯方块")
        self.width = 10
        self.height = 20
        self.cell_size = 30
        self.lines_cleared_total = [0, 0, 0]
        self.startspeed = 1000
        self.speed = [self.startspeed, self.startspeed, self.startspeed]
        self.game_over_flag = [False, False, False]
        self.paused = False
        self.shadow_enabled = [False, False, False]
        self.player_colors = ["blue", "red", "green"]
        self.game_mode = None 

        # --- 玩家1 ---
        self.canvas1 = tk.Canvas(root, width=self.width * self.cell_size, height=self.height * self.cell_size, bg="grey")
        self.canvas1.grid(row=0, column=0, rowspan=20)
        self.canvas1.create_rectangle(0, 0, self.width * self.cell_size, self.height * self.cell_size, fill=None, outline="black")
        self.next_canvas1 = tk.Canvas(root, width=4 * self.cell_size, height=4 * self.cell_size)
        self.next_canvas1.grid(row=0, column=1)
        self.score_label1 = tk.Label(root, text="玩家1分数: 0", font=("Arial", 16))
        self.score_label1.grid(row=1, column=1)

        # --- 玩家2 ---
        self.canvas2 = tk.Canvas(root, width=self.width * self.cell_size, height=self.height * self.cell_size, bg="grey")
        self.canvas2.grid(row=0, column=2, rowspan=20) # 修改布局，横向排列
        self.canvas2.create_rectangle(0, 0, self.width * self.cell_size, self.height * self.cell_size, fill=None, outline="black")
        self.next_canvas2 = tk.Canvas(root, width=4 * self.cell_size, height=4 * self.cell_size)
        self.next_canvas2.grid(row=0, column=3) # 修改布局，横向排列
        self.score_label2 = tk.Label(root, text="玩家2分数: 0", font=("Arial", 16))
        self.score_label2.grid(row=1, column=3) # 修改布局，横向排列

        # --- 玩家3 ---
        self.canvas3 = tk.Canvas(root, width=self.width * self.cell_size, height=self.height * self.cell_size, bg="grey")
        self.canvas3.grid(row=0, column=4, rowspan=20) #修改布局，横向排列
        self.canvas3.create_rectangle(0, 0, self.width * self.cell_size, self.height * self.cell_size, fill=None, outline="black")
        self.next_canvas3 = tk.Canvas(root, width=4 * self.cell_size, height=4 * self.cell_size)
        self.next_canvas3.grid(row=0, column=5) #修改布局，横向排列
        self.next_canvas3.grid_remove()
        self.score_label3 = tk.Label(root, text="玩家3分数: 0", font=("Arial", 16))
        self.score_label3.grid(row=1, column=5) #修改布局，横向排列

        self.next_canvas = tk.Canvas(root, width=4*self.cell_size, height=4*self.cell_size)
        self.next_canvas.grid(row=1, column=6)

        # 将记录列表和启动按钮移动到玩家3的下方
        self.high_score_label = tk.Label(root, text="最高分: 0", font=("Arial", 16))
        self.high_score_label.grid(row=2, column=5, columnspan=2) #修改布局
        
        self.rank_listbox = tk.Listbox(root, height=13, font=("Arial", 12), width=25)
        self.rank_listbox.grid(row=3, column=5, rowspan=15, columnspan=2) #修改布局
        
        self.choose_mode_button = tk.Button(root, text="选择模式", font=("Arial", 16), command=self.choose_game_mode, width=15)
        self.choose_mode_button.grid(row=19, column=5, columnspan=2) #修改布局
        
        self.start_button = tk.Button(root, text="开始游戏", font=("Arial", 16), command=self.start_game, width=15)
        self.start_button.grid(row=20, column=5, columnspan=2)
        self.start_button.grid_remove()

        self.high_scores = self.load_high_scores()
        self.update_high_score_label()
        self.update_rank_listbox()

        self.root.bind("<Key>", self.handle_keypress)
        self.paused_by_focus = False
        self.root.bind("<FocusOut>", self.pause_game_focus_out)
        self.root.bind("<FocusIn>", self.resume_game_focus_in)
        self.center_window(root)

    def choose_game_mode(self):
        def on_mode_select():
            self.game_mode = mode_var.get()
            mode_window.destroy()
            self.start_button.grid()
            self.choose_mode_button.grid_remove()
            if self.game_mode == 1:
                self.next_canvas1.grid_remove()
                self.next_canvas2.grid_remove()
                self.next_canvas3.grid_remove()
            else:
                self.next_canvas1.grid()
                self.next_canvas2.grid()
                self.next_canvas3.grid()

        mode_window = tk.Toplevel(self.root)
        mode_window.title("选择游戏模式")
        mode_var = tk.IntVar(value=0)
        self.center_window(mode_window)
        tk.Radiobutton(mode_window, text="正常模式", variable=mode_var, value=0).pack()
        tk.Radiobutton(mode_window, text="抢方块模式", variable=mode_var, value=1).pack()
        tk.Button(mode_window, text="确定", command=on_mode_select).pack()

    def center_window(self, window):
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        window.geometry(f"+{x}+{y}")

    def load_high_scores(self):
        if os.path.exists("highscores.json"):
            with open("highscores.json", "r") as f:
                return json.load(f)
        return []

    def save_high_scores(self):
        with open("highscores.json", "w") as f:
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

    def start_game(self):
        if self.game_mode is None:
            messagebox.showinfo("提示", "请先选择游戏模式！")
            return

        self.score = [0, 0, 0]
        self.board = [[[0 for _ in range(self.width)] for _ in range(self.height)] for _ in range(3)]
        self.current_tetromino = [None, None, None]
        if self.game_mode == 0:
            self.next_tetromino = [self.new_tetromino(), self.new_tetromino(), self.new_tetromino()]
        else:
            self.next_tetromino = self.new_tetromino()
        self.game_over_flag = [False, False, False]

        self.spawn_tetromino(0)
        self.spawn_tetromino(1)
        self.spawn_tetromino(2)
        self.update_canvas()
        self.update_next_canvas()

        self.score_label1.config(text="玩家1分数: 0")
        self.score_label2.config(text="玩家2分数: 0")
        self.score_label3.config(text="玩家3分数: 0")
        self.lines_cleared_total = [0, 0, 0]
        self.speed = [self.startspeed, self.startspeed, self.startspeed]
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
            if not self.game_over_flag[0]:
                self.move_tetromino(0, 0, 1)
            if not self.game_over_flag[1]:
                self.move_tetromino(1, 0, 1)
            if not self.game_over_flag[2]:
                self.move_tetromino(2, 0, 1)
            self.update_canvas()
        if not all(self.game_over_flag):
            self.root.after(min(self.speed), self.game_tick)

    def update_canvas(self):
        self.canvas1.delete("all")
        self.canvas2.delete("all")
        self.canvas3.delete("all")
        for player in range(3):
            if player == 0:
                canvas = self.canvas1
            elif player == 1:
                canvas = self.canvas2
            else:
                canvas = self.canvas3
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
            for i in range(3):
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
            if event.keysym == "a": 
                self.move_tetromino(0, -1, 0)
            elif event.keysym == "d":
                self.move_tetromino(0, 1, 0)
            elif event.keysym == "s":
                self.move_tetromino(0, 0, 1)
            elif event.keysym == "w":
                self.rotate_tetromino(0)
            elif event.keysym == "space":
                self.drop_tetromino(0)
            elif event.keysym == "Left":
                self.move_tetromino(2, -1, 0)
            elif event.keysym == "Right":
                self.move_tetromino(2, 1, 0)
            elif event.keysym == "Down": 
                self.drop_tetromino(2)
            elif event.keysym == "Up":
                self.rotate_tetromino(2)
            elif event.keysym == "j":
                self.move_tetromino(1, -1, 0)
            elif event.keysym == "l":
                self.move_tetromino(1, 1, 0)
            elif event.keysym == "i":
                self.rotate_tetromino(1)
            #elif event.keysym == "k":
            #    self.move_tetromino(1, 0,1)
            elif event.keysym == "k":
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
            
if __name__ == "__main__":
    root = tk.Tk()
    game = Tetris(root)
    root.mainloop()
