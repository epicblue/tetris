# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import simpledialog
import random
import os
import json
from datetime import datetime

class Tetris:
    def __init__(self, root):
        self.root = root
        self.root.title("俄罗斯方块")
        self.width = 10
        self.height = 20
        self.cell_size = 30

        self.canvas = tk.Canvas(root, width=self.width * self.cell_size, height=self.height * self.cell_size, bg="lightgrey")
        self.canvas.grid(row=0, column=0, rowspan=20)
        self.canvas.create_rectangle(0, 0, self.width * self.cell_size, self.height * self.cell_size, fill=None, outline="black")
        
        self.next_canvas = tk.Canvas(root, width=4 * self.cell_size, height=4 * self.cell_size)
        self.next_canvas.grid(row=0, column=1)

        self.score_label = tk.Label(root, text="分数: 0", font=("Arial", 16))
        self.score_label.grid(row=1, column=1)

        self.high_score_label = tk.Label(root, text="最高分: 0", font=("Arial", 16))
        self.high_score_label.grid(row=2, column=1)

        self.rank_listbox = tk.Listbox(root, height=10, font=("Arial", 12))
        self.rank_listbox.grid(row=3, column=1)

        self.start_button = tk.Button(root, text="开始游戏", font=("Arial", 16), command=self.start_game)
        self.start_button.grid(row=13, column=1)

        self.paused = False  # 添加一个暂停标志
        self.game_over_flag = False  # 添加一个游戏结束标志
        self.shadow_enabled = False  # 添加阴影功能的使能标志，默认关闭

        self.high_scores = self.load_high_scores()  # 加载最高分数记录
        self.update_high_score_label()
        self.update_rank_listbox()

        self.root.bind("<Key>", self.handle_keypress)

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
        self.score = 0
        self.board = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.current_tetromino = None
        self.next_tetromino = self.new_tetromino()
        self.game_over_flag = False  # 重新开始游戏时重置游戏结束标志

        self.spawn_tetromino()
        self.update_canvas()
        self.update_next_canvas()

        self.score_label.config(text="分数: 0")
        self.root.after(500, self.game_tick)

        # 隐藏“开始游戏”按钮
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

    def spawn_tetromino(self):
        self.current_tetromino = self.next_tetromino
        self.next_tetromino = self.new_tetromino()
        self.update_next_canvas()  # 确保在生成新的下一个方块后更新预览画布
        if not self.is_valid_position(self.current_tetromino):
            self.game_over()

    def is_valid_position(self, tetromino, dx=0, dy=0):
        for y, row in enumerate(tetromino['shape']):
            for x, cell in enumerate(row):
                if cell:
                    new_x = tetromino['x'] + x + dx
                    new_y = tetromino['y'] + y + dy
                    if new_x < 0 or new_x >= self.width or new_y >= self.height:
                        return False
                    if new_y >= 0 and self.board[new_y][new_x]:
                        return False
        return True

    def place_tetromino(self):
        for y, row in enumerate(self.current_tetromino['shape']):
            for x, cell in enumerate(row):
                if cell:
                    self.board[self.current_tetromino['y'] + y][self.current_tetromino['x'] + x] = self.current_tetromino['color']
        self.clear_lines()
        self.spawn_tetromino()

    def clear_lines(self):
        new_board = [row for row in self.board if not all(row)]
        lines_cleared = self.height - len(new_board)
        self.score += lines_cleared * 10
        self.score_label.config(text=f"分数: {self.score}")
        new_board = [[0] * self.width for _ in range(lines_cleared)] + new_board
        self.board = new_board

    def rotate_tetromino(self):
        rotated_shape = list(zip(*self.current_tetromino['shape'][::-1]))
        rotated_tetromino = {'shape': rotated_shape, 'color': self.current_tetromino['color'], 'x': self.current_tetromino['x'], 'y': self.current_tetromino['y']}
        if self.is_valid_position(rotated_tetromino):
            self.current_tetromino = rotated_tetromino

    def move_tetromino(self, dx, dy):
        if self.is_valid_position(self.current_tetromino, dx, dy):
            self.current_tetromino['x'] += dx
            self.current_tetromino['y'] += dy
        elif dy > 0:
            self.place_tetromino()

    def game_tick(self):
        if not self.paused and not self.game_over_flag:  # 只在未暂停且未结束时更新方块状态
            self.move_tetromino(0, 1)
            self.update_canvas()
        self.root.after(500, self.game_tick)

    def update_canvas(self):
        self.canvas.delete("all")
        # 先画板上的方块
        for y, row in enumerate(self.board):
            for x, cell in enumerate(row):
                if cell:
                    self.draw_cell(self.canvas, x, y, cell)

        # 画方块阴影
        if self.shadow_enabled:  # 仅当阴影功能使能时绘制阴影
            shadow_tetromino = self.get_shadow_tetromino()
            for y, row in enumerate(shadow_tetromino['shape']):
                for x, cell in enumerate(row):
                    if cell:
                        self.draw_cell(self.canvas, shadow_tetromino['x'] + x, shadow_tetromino['y'] + y, "lightgrey")

        # 画当前方块
        for y, row in enumerate(self.current_tetromino['shape']):
            for x, cell in enumerate(row):
                if cell:
                    self.draw_cell(self.canvas, self.current_tetromino['x'] + x, self.current_tetromino['y'] + y, self.current_tetromino['color'])

    def update_next_canvas(self):
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

    def get_shadow_tetromino(self):
        shadow = {'shape': self.current_tetromino['shape'], 'color': self.current_tetromino['color'], 'x': self.current_tetromino['x'], 'y': self.current_tetromino['y']}
        while self.is_valid_position(shadow, dy=1):
            shadow['y'] += 1
        return shadow

    def drop_tetromino(self):
        while self.is_valid_position(self.current_tetromino, dy=1):
            self.current_tetromino['y'] += 1
        self.place_tetromino()
        self.update_canvas()
        
    def handle_keypress(self, event):
        if event.keysym == "p" or event.keysym == "P":  # 检测按下"P"键
            self.paused = not self.paused  # 切换暂停状态
            if self.paused:
                self.canvas.create_text(self.width * self.cell_size // 2, self.height * self.cell_size // 2,
                                        text="暂停", fill="green", font=("Arial", 24))
            else:
                self.update_canvas()  # 继续游戏时，更新画布清除
        elif event.keysym == "s" or event.keysym == "S":  # 检测按下"S"键
            self.shadow_enabled = not self.shadow_enabled  # 切换阴影功能状态
            self.update_canvas()  # 切换阴影功能时重新绘制画布
        elif not self.paused:  # 如果没暂停，才处理其他按键
            if event.keysym == "Left":
                self.move_tetromino(-1, 0)
            elif event.keysym == "Right":
                self.move_tetromino(1, 0)
            elif event.keysym == "Down":
                self.move_tetromino(0, 1)
            elif event.keysym == "Up":
                self.rotate_tetromino()
            elif event.keysym == "space":
                self.drop_tetromino()  # 修改为立即下落
            self.update_canvas()

    def game_over(self):
        self.game_over_flag = True
        self.canvas.create_text(self.width * self.cell_size // 2, self.height * self.cell_size // 2,
                                text="游戏结束", fill="red", font=("Arial", 24))
        
        # 获取玩家名称
        player_name = simpledialog.askstring("输入名称", "请输入您的名称:")
        if not player_name:
            player_name = "匿名玩家"

        # 记录当前时间
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 添加当前分数到排名
        new_entry = {"name": player_name, "score": self.score, "date": current_time}
        self.high_scores.append(new_entry)
        # 按分数排序
        self.high_scores = sorted(self.high_scores, key=lambda x: x["score"], reverse=True)[:10]

        # 保存并更新
        self.save_high_scores()
        self.update_high_score_label()
        self.update_rank_listbox()

        # 取消游戏的定时器
        self.root.after_cancel(self.game_tick)
        
        # 显示“开始游戏”按钮
        self.start_button.grid()

if __name__ == "__main__":
    root = tk.Tk()
    game = Tetris(root)
    root.mainloop()
