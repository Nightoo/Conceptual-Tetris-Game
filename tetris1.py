import sys
from random import randint
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import Qt,  QBasicTimer

# 0 - empty
# 1 - filled

SPEED = 150  # the less speed is the faster the game runs
WIDTH = 30  # of one cell
HEIGHT = 30  # of one cell
FIELD_HEIGHT = 21  # at least 8
FIELD_WIDTH = 10  # at least 6
# field's generation
FIELD = []
for _ in range(FIELD_HEIGHT):
    FIELD.append([0 for __ in range(FIELD_WIDTH)])
FIELD.append([1 for ___ in range(FIELD_WIDTH)])
DEADLINE = 4


class Coords:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Figures:
    # third element in every figure's coordinates is rotation point
    Square = [Coords(4, 2), Coords(5, 2), Coords(4, 3), Coords(5, 3)]
    IFigure = [Coords(5, 0), Coords(5, 1), Coords(5, 2), Coords(5, 3)]
    TFigure = [Coords(4, 2), Coords(3, 3), Coords(4, 3), Coords(5, 3)]
    SFigure = [Coords(5, 2), Coords(4, 2), Coords(4, 3), Coords(3, 3)]
    ZFigure = [Coords(4, 2), Coords(5, 2), Coords(5, 3), Coords(6, 3)]
    LFigure = [Coords(4, 1), Coords(4, 3), Coords(4, 2), Coords(5, 3)]
    GammaFigure = [Coords(4, 3), Coords(5, 3), Coords(5, 2), Coords(5, 1)]

    def get_random_figure(self):
        number = randint(1, 7)
        if number == 1:
            return self.Square
        elif number == 2:
            return self.IFigure
        elif number == 3:
            return self.TFigure
        elif number == 4:
            return self.SFigure
        elif number == 5:
            return self.ZFigure
        elif number == 6:
            return self.LFigure
        elif number == 7:
            return self.GammaFigure


class Shape:
    def __init__(self, parts):
        self.parts = parts
        self.R = randint(0, 255)
        self.G = randint(0, 255)
        self.B = randint(0, 255)

    def erase(self):
        for part in self.parts:
            FIELD[part.y][part.x] = 0

    def spawn(self):
        for part in self.parts:
            FIELD[part.y][part.x] = 1

    def move(self, step_x, step_y):
        coord_after_movement = []
        for part in self.parts:
            if part.x + step_x < 0 or part.x + step_x >= len(FIELD[0]):
                return
            if part.y + step_y < 0 or part.y + step_y >= len(FIELD):
                return
            coord_after_movement.append(Coords(part.x + step_x, part.y + step_y))
        self.erase()
        possible = True
        for part in coord_after_movement:
            skip = False
            for last_part in self.parts:
                if part.x == last_part.x and part.y == last_part.y:
                    skip = True
                    break
            if skip:
                continue
            if FIELD[part.y][part.x] == 1:
                possible = False
                break
        if possible:
            self.parts = coord_after_movement
        self.spawn()

    def move_left(self):
        self.move(-1, 0)

    def move_right(self):
        self.move(1, 0)

    def move_down(self):
        self.move(0, 1)

    def rotate(self, rotate):
        if self.parts[0].x == self.parts[2].x and self.parts[1].x == self.parts[3].x \
                and self.parts[0].y == self.parts[1].y and self.parts[2].y == self.parts[3].y:
            return
        coords_after_rotation = []
        for part in self.parts:
            part_x_copy = part.x
            new_x = (rotate * part.y - rotate * self.parts[2].y) + self.parts[2].x
            if new_x < 0 or new_x >= len(FIELD[0]):
                return
            new_y = (-rotate * part_x_copy + rotate * self.parts[2].x) + self.parts[2].y
            if new_y < 0 or new_y >= len(FIELD):
                return
            coords_after_rotation.append(Coords(new_x, new_y))
        self.erase()
        possible = True
        for part in coords_after_rotation:
            skip = False
            for last_part in self.parts:
                if part.x == last_part.x and part.y == last_part.y:
                    skip = True
                    break
            if skip:
                continue
            if FIELD[part.y][part.x] == 1:
                possible = False
                break
        if possible:
            self.parts = coords_after_rotation
        self.spawn()

    def rotate_right(self):
        self.rotate(1)

    def rotate_left(self):
        self.rotate(-1)


shape = Shape(Figures().get_random_figure())


class Game(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.game_over = False
        self.paused = False
        self.score = 0

    def initUI(self):
        self.setGeometry(300, 300, FIELD_WIDTH * WIDTH, FIELD_HEIGHT * HEIGHT)
        self.setWindowTitle('Концептуальный Тетрис')
        self.show()
        self.timer = QBasicTimer()
        self.timer.start(SPEED, self)

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        if self.game_over:
            for y in range(len(FIELD) - 1):
                for x in range(len(FIELD[0])):
                    qp.setBrush(QColor(255, 0, 0))
                    qp.drawRect(x * WIDTH, y * HEIGHT, WIDTH, HEIGHT)
        else:
            for y in range(len(FIELD) - 1):
                for x in range(len(FIELD[0])):
                    if FIELD[y][x] == 0:
                        qp.setBrush(QColor(0, 0, 0))
                        qp.drawRect(x * WIDTH, y * HEIGHT, WIDTH, HEIGHT)
                    for i in range(len(shape.parts)):
                        if x == shape.parts[i].x and y == shape.parts[i].y:
                            qp.setBrush(QColor(shape.R, shape.G, shape.B))
                            qp.drawRect(x * WIDTH, y * HEIGHT, WIDTH, HEIGHT)

    def pause(self):
        if self.paused:
            self.timer.start(SPEED, self)
            self.paused = False
        else:
            self.timer.stop()
            self.paused = True
        self.update()

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_D:
            shape.move_right()
        if key == Qt.Key_A:
            shape.move_left()
        if key == Qt.Key_E:
            shape.rotate_right()
        if key == Qt.Key_Q:
            shape.rotate_left()
        if key == Qt.Key_S:
            shape.move_down()
        if key == Qt.Key_P:
            self.pause()

    def timerEvent(self, event):
        global shape
        y_check = shape.parts[0].y
        shape.move_down()
        self.update()
        if shape.parts[0].y == y_check:
            shape = Shape(Figures().get_random_figure())
            self.check_fullfilled_lines()
            if 1 in FIELD[DEADLINE]:
                self.game_over = True

    def check_fullfilled_lines(self):
        for y in range(len(FIELD) - 1):
            if FIELD[y].count(1) == len(FIELD[y]):
                FIELD.remove(FIELD[y])
                self.score += 10
                FIELD.insert(0, [0 for _ in range(len(FIELD[1]))])


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Game()
    ex.show()
    sys.exit(app.exec())
