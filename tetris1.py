import sys
import sqlite3
from random import randint
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QLabel, QLineEdit
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import Qt,  QBasicTimer

# 0 - empty
# 1 - filled

PLAYER_NAME = None
PLAYER_SCORE = 0
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


class Game(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.game_over = False
        self.paused = False

    def initUI(self):
        self.setGeometry(200, 200, FIELD_WIDTH * WIDTH, FIELD_HEIGHT * HEIGHT)
        self.setWindowTitle('Conceptual Tetris')
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
                self.finish_game()

    def check_fullfilled_lines(self):
        for y in range(len(FIELD) - 1):
            if FIELD[y].count(1) == len(FIELD[y]):
                FIELD.remove(FIELD[y])
                global PLAYER_SCORE
                PLAYER_SCORE += 10
                FIELD.insert(0, [0 for _ in range(len(FIELD[1]))])

    def finish_game(self):
        self.timer.stop()
        self.enter_your_name = EnterYourName()
        self.enter_your_name.show()


class EnterYourName(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 160, 90)
        self.setWindowTitle('Enter your name')

        self.confirm_button = QPushButton('Confirm', self)
        self.confirm_button.resize(80, 30)
        self.confirm_button.move(10, 55)
        self.confirm_button.clicked.connect(self.confirmation)

        self.name_label = QLabel(self)
        self.name_label.setText("Enter your name")
        self.name_label.move(10, 10)

        self.name_input = QLineEdit(self)
        self.name_input.move(10, 25)

    def confirmation(self):
        global PLAYER_NAME
        PLAYER_NAME = self.name_input.text()
        self.data_base = DataBase()
        self.data_base.show()


class DataBase(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(250, 250, 220, 150)
        self.setWindowTitle('Leaderboard')

        self.score_label = QLabel(self)
        self.score_label.setText('Your score: {}'.format(PLAYER_SCORE))
        self.score_label.move(10, 10)

        self.name1 = QLabel(self)
        self.name1.move(10, 40)
        self.name2 = QLabel(self)
        self.name2.move(10, 50)
        self.name3 = QLabel(self)
        self.name3.move(10, 60)
        self.name4 = QLabel(self)
        self.name4.move(10, 70)
        self.name5 = QLabel(self)
        self.name5.move(10, 80)
        self.name6 = QLabel(self)
        self.name6.move(10, 90)
        self.name7 = QLabel(self)
        self.name7.move(10, 100)
        self.name8 = QLabel(self)
        self.name8.move(10, 110)
        self.name9 = QLabel(self)
        self.name9.move(10, 120)
        self.name10 = QLabel(self)
        self.name10.move(10, 130)

        self.score1 = QLabel(self)
        self.score1.move(100, 40)
        self.score2 = QLabel(self)
        self.score2.move(100, 50)
        self.score3 = QLabel(self)
        self.score3.move(100, 60)
        self.score4 = QLabel(self)
        self.score4.move(100, 70)
        self.score5 = QLabel(self)
        self.score5.move(100, 80)
        self.score6 = QLabel(self)
        self.score6.move(100, 90)
        self.score7 = QLabel(self)
        self.score7.move(100, 100)
        self.score8 = QLabel(self)
        self.score8.move(100, 110)
        self.score9 = QLabel(self)
        self.score9.move(100, 120)
        self.score10 = QLabel(self)
        self.score10.move(100, 130)

        self.add = QPushButton('Add to a leaderboard', self)
        self.add.resize(110, 30)
        self.add.move(100, 10)
        self.add.clicked.connect(self.add_data)

    def add_data(self):
        self.add.setText('Successfully added')
        self.add.setEnabled(False)
        conn = sqlite3.connect('leaderboard1.db')
        cur = conn.cursor()
        global PLAYER_NAME, PLAYER_SCORE
        cur.execute('INSERT INTO leadertable(name, score) VALUES(?, ?)', (PLAYER_NAME, PLAYER_SCORE))
        self.results_name = cur.execute('SELECT name FROM leadertable ORDER BY score DESC').fetchmany(10)
        self.results_score = cur.execute('SELECT score FROM leadertable ORDER BY score DESC').fetchmany(10)
        print(self.results_name)
        print(self.results_score)
        conn.commit()
        cur.close()
        conn.close()
        self.show_results()

    def show_results(self):
        self.name1.setText('{}'.format(self.results_name[0][0]))
        self.name1.resize(self.name1.sizeHint())
        self.score1.setText('{}'.format(self.results_score[0][0]))
        self.score1.resize(self.score1.sizeHint())
        self.name2.setText('{}'.format(self.results_name[1][0]))
        self.name2.resize(self.name2.sizeHint())
        self.score2.setText('{}'.format(self.results_score[1][0]))
        self.score2.resize(self.score2.sizeHint())
        self.name3.setText('{}'.format(self.results_name[2][0]))
        self.name3.resize(self.name3.sizeHint())
        self.score3.setText('{}'.format(self.results_score[2][0]))
        self.score3.resize(self.score3.sizeHint())
        self.name4.setText('{}'.format(self.results_name[3][0]))
        self.name4.resize(self.name4.sizeHint())
        self.score4.setText('{}'.format(self.results_score[3][0]))
        self.score4.resize(self.score4.sizeHint())
        self.name5.setText('{}'.format(self.results_name[4][0]))
        self.name5.resize(self.name5.sizeHint())
        self.score5.setText('{}'.format(self.results_score[4][0]))
        self.score5.resize(self.score5.sizeHint())
        self.name6.setText('{}'.format(self.results_name[5][0]))
        self.name6.resize(self.name6.sizeHint())
        self.score6.setText('{}'.format(self.results_score[5][0]))
        self.score6.resize(self.score6.sizeHint())
        self.name7.setText('{}'.format(self.results_name[6][0]))
        self.name7.resize(self.name7.sizeHint())
        self.score7.setText('{}'.format(self.results_score[6][0]))
        self.score7.resize(self.score7.sizeHint())
        self.name8.setText('{}'.format(self.results_name[7][0]))
        self.name8.resize(self.name8.sizeHint())
        self.score8.setText('{}'.format(self.results_score[7][0]))
        self.score8.resize(self.score8.sizeHint())
        self.name9.setText('{}'.format(self.results_name[8][0]))
        self.name9.resize(self.name9.sizeHint())
        self.score9.setText('{}'.format(self.results_score[8][0]))
        self.score9.resize(self.score9.sizeHint())
        self.name10.setText('{}'.format(self.results_name[9][0]))
        self.name10.resize(self.name10.sizeHint())
        self.score10.setText('{}'.format(self.results_score[9][0]))
        self.score10.resize(self.score10.sizeHint())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Game()
    ex.show()
    sys.exit(app.exec())
