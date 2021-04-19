from tkinter import *
import time
import random


class Score:
    """""
    Класс Score.
    Служит для отображения очков, заработанных во время игры.
    Один разбитый кирпич -> + 1 очко. Сумма очков изображена в правом верхнем углу. 
    """""
    def __init__(self, canvas):
        self.score = 0
        self.canvas = canvas
        self.table = canvas.create_text(450, 10, text=self.score, font=('Courier', 15), fill='black')

    def hit(self):
        self.score += 1
        self.canvas.itemconfig(self.table, text=self.score)


class Platform:
    def __init__(self, canvas):
        """
        В конструкторе создаётся прямоугольник 100 на 10 пикселей зелёного цвета, перемещается на позицию 400 400.
        """
        self.canvas = canvas
        self.plat = canvas.create_rectangle(0, 0, 100, 10, fill='green', outline="")
        self.start = 400
        self.canvas.move(self.plat, self.start, 400)
        self.x = 0
        self.canvas_width = self.canvas.winfo_width()
        self.canvas.bind_all('<KeyPress-Right>', lambda event: self.handle_turn(1, True))
        self.canvas.bind_all('<KeyRelease-Right>', lambda event: self.handle_turn(1, False))
        self.canvas.bind_all('<KeyPress-Left>', lambda event: self.handle_turn(-1, True))
        self.canvas.bind_all('<KeyRelease-Left>', lambda event: self.handle_turn(-1, False))

    def handle_turn(self, direction, press_state):
        """
         Получает направление и состояние кнопки клавиатуры.
         Двигает платформу при нажатии/удерживании кнопки влево/вправо, останавливает при отжатии.
        """
        speed = 500
        if press_state:
            self.x = speed * direction
        elif self.x * direction > 0:
            self.x = 0

    def draw(self, delta_time):
        """
        Ограничивает движение платформы, не давая ей выйти за пределы окна.
        """
        pos = self.canvas.coords(self.plat)
        shift = self.x * delta_time
        if pos[0] + shift <= 0 or pos[2] + shift >= self.canvas_width:
            return
        self.canvas.move(self.plat, shift, 0)


class Brick:
    def __init__(self, canvas, x, y, color):
        """
        В конструкторе создаётся прямоугольник синего цвета 50x50, который перемещается на позицию x, y.
        broken - флаг обозначающий состояние кирпича на экране.
        """
        self.canvas = canvas
        self.brick = canvas.create_rectangle(250, 300, 300, 250, fill=color)
        self.canvas.move(self.brick, x, y)
        self.canvas_height = self.canvas.winfo_height()
        self.canvas_width = self.canvas.winfo_width()
        self.broken = False

    def draw(self):
        """
        Уничтожает кирпич, если он был сломан
        """
        if self.broken:
            self.canvas.delete(self.brick)


class Ball:
    def __init__(self, canvas, plat, bricks, score):
        """
        В конструкторе создаётся шар 10х10х25х25(?) красного цвета.
        Перемещается на позицию 245 100.
        Задаётся начальная скорость движения шара: 250 по х, -125 по у.
        Переменные last_tact (вспомогательный флаг для счёта) и fallen (не упал ли шар на дно) инициализируются false.
        wind_cond - счётчик разбитых кирпичей.
        """
        self.canvas = canvas
        self.platform = plat
        self.score = score
        self.bricks = bricks
        self.ball = canvas.create_oval(10, 10, 25, 25, fill='red', outline='white')
        self.canvas.move(self.ball, 245, 100)
        self.x = 250
        self.y = 125
        self.canvas_height = self.canvas.winfo_height()
        self.canvas_width = self.canvas.winfo_width()
        self.last_tact = False
        self.fallen = False
        self.win_cond = 0

    def hit_plat(self, pos):
        """
        Если мяч попадает на платформу, то возвращается true.
        """
        plat_pos = self.canvas.coords(self.platform.plat)
        if pos[2] >= plat_pos[0] and pos[0] <= plat_pos[2] and plat_pos[1] <= pos[3] <= plat_pos[3]:
            return True
        return False

    def hit_brick(self, pos, i):
        """
        Если мяч касается кирпича, last_tact меняет значение, счётчик увеличивается на один.
        """
        brick_pos = self.canvas.coords(self.bricks[i].brick)
        if pos[2] >= brick_pos[0] and pos[0] <= brick_pos[2] and brick_pos[1] <= pos[3] <= brick_pos[3]:
            if not self.last_tact:
                self.score.hit()
                self.last_tact = True
            return True
        return False

    def draw(self, delta_time):
        """
        Шарик перемещается с определенной скоростью.
        Если шарик касается верхней стенки, то он отскакивает вниз.
        Если шарик выпадает за пределы, fallen = true, игра выводит сообщение 'Game Over'.
        Если мяч отскочил от кирпича, brick.broken = true, win_cond увеличивается на 1.
        Если кирпича не тронул, отскакивает от стенок.
        В зависимости от стороны платформы на которую попал шар, он отлетает в разных направлениях.
        Когда счётчик win_cond достигнет кол-ва кирпичей, игрок побеждает, выводится надпись "Congratulations".
        """
        shift_x = self.x * delta_time
        shift_y = self.y * delta_time
        self.canvas.move(self.ball, shift_x, shift_y)
        pos = self.canvas.coords(self.ball)
        if pos[1] <= 0:
            self.y = 125
        if pos[3] >= self.canvas_height:
            self.fallen = True
            self.canvas.create_text(250, 120, text='Game Over', font=('Courier', 30), fill='black')
        for i in range(10):
            if not self.bricks[i].broken:
                if self.hit_brick(pos, i):
                    self.win_cond += 1
                    self.y = 125
                    self.bricks[i].broken = True
                else:
                    if pos[0] <= 0:
                        self.x = 250
                    if pos[3] >= self.canvas_height:
                        self.y = 250
                    if pos[2] >= self.canvas_width:
                        self.x = -250
                    self.last_tact = False
        if self.hit_plat(pos):
            self.y = -125
        else:
            if pos[0] <= 0:
                self.x = 250
            if pos[2] >= self.canvas_width:
                self.x = -250
        if self.win_cond == 10:
            self.canvas.create_text(250, 120, text='Congratulations', font=('Courier', 30), fill='black')
            self.fallen = True


def start_game(platform, bricks, ball):
    """
    Платформа, кирпичи и мяч приводятся в активное положение.
    Замеряется текущее время, чтобы скорость движения шара зависела от времени.
    Пока не упал мяч: используем методы draw у каждого из объектов.
    """
    current_time = time.monotonic()
    while not ball.fallen:
        after_iter_time = time.monotonic()
        delta = after_iter_time - current_time
        if platform.start:
            platform.draw(delta)
            ball.draw(delta)
            for i in range(10):
                bricks[i].draw()
        window.update_idletasks()
        window.update()
        current_time = after_iter_time


"""
В основе программы создаётся окно 500х500 с названием игры.
Инициализируются score, платформа, мяч и список из 10 кирпичей: 5 синих и 5 жёлтых.
"""
window = Tk()
window.title('Arkanoid: early version')
window.resizable(0, 0)
window.wm_attributes('-topmost', 1)
canvas_ = Canvas(window, width=500, height=500, highlightthickness=0)
canvas_.pack()
window.update()
score = Score(canvas_)
platform = Platform(canvas_)
brick_lst = [Brick(canvas_, -250 + 100 * _, -230, 'blue') for _ in range(5)]
for i in range(5):
    brick_lst.append(Brick(canvas_, -200 + 100 * i, -180, 'yellow'))
ball = Ball(canvas_, platform, brick_lst, score)
start_game(platform, brick_lst, ball)
