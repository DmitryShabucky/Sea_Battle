from random import randint
from random import choice
from time import sleep


class BoardException(Exception):
    """Родительский класс несуществующих исключений"""
    pass


class BoardOutException(BoardException):
    """Выстрел мимо поля"""

    def __str__(self):
        return f"{' ' * 20}Вы стреляете мимо поля!"


class BoardUsedException(BoardException):
    """Выстрел в занятую клетку"""

    def __str__(self):
        return f"{' ' * 21}Вы туда уже стреляли!"


class BoardWrongShipException(BoardException):
    """Нет возможности разместить корабль на поле"""
    pass


class Dot:
    """Создает координаты выстрела"""

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        """Сравнивает координаты точек"""
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        """Возвращает координаты выстрела"""
        return f"Dot({self.x}, {self.y})"


class Ship:
    """Создает корабль, в зависимости от его длины и направления"""

    def __init__(self, bow, l, o):
        self.bow = bow
        self.l = l
        self.o = o
        self.lives = l

    @property
    def dots(self):
        """Возвращает список с координатами кораблей"""
        ship_dots = []
        for i in range(self.l):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.o == 0:
                cur_x += i

            elif self.o == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    def shooten(self, shot):
        """Проверяет наличие координат выстрела в списке точек корабля"""
        return shot in self.dots


class Board:
    """Создает игровую доску со списком кораблей"""

    def __init__(self, size=6):
        self.size = size

        self.count = 0  # счетчик уничтоженных кораблей
        self.field = [["O"] * size for _ in range(size)]  # матрица игрового поля
        self.busy = []  # список занятых точек
        self.ships = []  # список кораблей на поле
        self.hit_ship = []  # список точек раненного корабля
        self.vert_dots = []  # список соседних с попаданием точек по вертикали
        self.hor_dots = []  # список соседних с попаданием точек по горизонтали
        self.hor_vert_dots = []  # список всех соседних с попаданием точек

    def __iter__(self):
        """Создает итерируемое игровое поле"""
        self.current = 0
        return self

    def __next__(self):
        """Создает итерируемое игровое поле"""
        if self.current == self.size:
            raise StopIteration
        else:
            matrix = f"{' | '.join(map(str, self.field[self.current]))} |"
            self.current += 1
            return matrix

    def __getitem__(self, item):
        """Дает возможность обратиться к элементам поля по индексу"""
        return self.field[item]

    def out(self, d):
        """Проверяет попадание выстрела в доску"""
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def contour(self, ship, verb=False):
        """Задает границы вокруг корабля"""
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    def add_ship(self, ship, hid=False):
        """Добавляет корабль на поле"""
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            if not hid:
                self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def shot(self, d, comp=False):
        """Производит выстрел с попыткой добить корабль"""
        for dot in self.hor_vert_dots:  # убирает точки раненого корабля из списка точек на добивание
            if dot in self.hit_ship:
                self.hor_vert_dots.remove(dot)

        for dot in self.hor_vert_dots:  # убирает точки в списке использованных из списка точек на добивание
            if dot in self.busy:
                self.hor_vert_dots.remove(dot)

        if comp:  # условие, при котором ход ИИ
            if len(self.hor_vert_dots) > 0 and d not in self.hor_vert_dots:  # выбор координат выстрела из списка
                d = choice(self.hor_vert_dots)  # точек на добивание, если он не пустой
                self.hor_vert_dots.remove(d)
            elif d in self.busy:  # генерирует координаты выстрела вне списка использованных точек
                while d in self.busy:
                    d = Dot(randint(0, 5), randint(0, 5))
            print("=" * 62)
            print(f"Ходит компьютер! {d.x + 1} {d.y + 1}")
        if d in self.busy:  # проверка на попадание в список использованных точек
            raise BoardUsedException()

        if self.out(d):  # проверка на попадание в игровое поле
            raise BoardOutException()

        self.busy.append(d)  # обновление списка использованных точек

        for ship in self.ships:  # проверка на попадание в корабль
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    if comp:  # условие, при котором ход ИИ
                        self.hor_dots = []
                        self.vert_dots = []
                        self.hit_ship = []
                        self.hor_vert_dots = []
                        print()
                        print(f"{'*' * 21} Корабль уничтожен! {'*' * 21}")
                        print()
                        return True
                    print()
                    print(f"{'*' * 21} Корабль уничтожен! {'*' * 21}")
                    print()
                    return True

                elif comp:  # условие, при котором ход ИИ
                    self.hit_ship.append(d)
                    horizontals = [(0, -1), (0, 1)]
                    verticals = [(-1, 0), (1, 0)]

                    for dx, dy in horizontals:  # создает список соседних от попадания точек по горизонтали
                        cur = Dot(dx + d.x, dy + d.y)
                        if self.out(cur):
                            pass
                        else:
                            self.hor_dots.append(cur)

                    for dx, dy in verticals:  # создает список соседних от попадания точек по вертикати
                        cur = Dot(dx + d.x, dy + d.y)
                        if self.out(cur):
                            pass
                        else:
                            self.vert_dots.append(cur)

                    if len(self.hit_ship) > 1:  # в случае повторного попадания в корабль, производит
                        for i in self.hit_ship[0:1]:  # определение направления корабля и удаляет ненужные
                            dot = i  # точки из списка на добивание
                            for j in self.hit_ship[1:2]:
                                if j.x == dot.x:
                                    self.vert_dots = []
                                else:
                                    self.hor_dots = []

                    self.hor_vert_dots = self.hor_dots + self.vert_dots  # обновление списка на добивание

                    print()
                    print(f"{'-*' * 12} Корабль ранен! {'*-' * 11}")
                    print()
                    return True

                else:
                    print()
                    print(f"{'-*' * 12} Корабль ранен! {'*-' * 11}")
                    print()
                    return True

        self.field[d.x][d.y] = "."
        print()
        print(f"{'-' * 28} Мимо! {'-' * 27}")
        print()
        return False

    def begin(self):
        """Обнуляет список использованных точек"""
        self.busy = []


class Player:
    """Класс игрока"""

    def __init__(self, board, enemy):
        """Принимает доску пользователя и компьютера"""
        self.board = board
        self.enemy = enemy

    def ask(self):
        """Условия в наследуемом классе"""
        raise NotImplementedError()

    def move(self, comp=False):
        """Производит выстрел"""
        while True:
            try:
                if comp:  # условие, при котором ход ИИ
                    target = self.ask()
                    repeat = self.enemy.shot(target, comp=True)
                else:
                    target = self.ask()
                    repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    """Класс ИИ"""

    def ask(self):
        """Возвращает координаты выстрела"""
        d = Dot(randint(0, 5), randint(0, 5))
        return d


class User(Player):
    """Класс пользователь"""

    def ask(self):
        """Возращает координаты выстрела"""
        while True:
            print("=" * 62)
            cords = input(f"{' ' * 33}Ваш ход: ").split()

            if len(cords) != 2:
                print(f"{' ' * 22}Введите 2 координаты!")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(f"{' ' * 25}Введите числа!")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


class Game:
    """Класс игрового процесса"""
    def __init__(self, size=6):
        self.size = size

        pl = self.random_board()
        co = self.random_board(hid=True)

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def try_board(self, hid=False):
        """Пробует создать игровое поле"""
        lens = [3, 2, 2, 1, 1, 1, 1]  # список длин кораблей
        board = Board(size=self.size)
        attempts = 0  # счетчик попыток создания доски
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    if hid:  # условие, при котором корабли противника не видны на доске
                        board.add_ship(ship, hid=True)
                    else:
                        board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def random_board(self, hid=False):
        """Создает доску вне зависимости от числа попыток"""
        board = None
        while board is None:
            if hid:  # условие, при котором корабли противника не видны на доске
                board = self.try_board(hid=True)
            else:
                board = self.try_board()
        return board

    def print_field(self):
        """Печатает доски в консоли"""
        a = """=============================    =============================
      ПОЛЕ ПОЛЬЗОВАТЕЛЯ                 ПОЛЕ КОМПЬЮТЕРА
=============================    =============================
    | 1 | 2 | 3 | 4 | 5 | 6 |        | 1 | 2 | 3 | 4 | 5 | 6 |"""

        print(a)
        for i, val in enumerate(self.us.board):
            print(f"| {i + 1} | {val}    | {i + 1} | {' | '.join(map(str, self.ai.board[i]))} |")

    def greet(self):
        """Печатает в консоли припетствие"""
        print()
        print('*' * 62)
        print(f'*{" " * 22}Игра Морской Бой{" " * 22}*')
        print('*' * 62)
        print(f'*{" " * 19} Координаты хода: Х и У{" " * 18}*')
        print(f'*{" " * 22} Х - это строчка{" " * 22}*')
        print(f'*{" " * 22} У - это столбик{" " * 22}*')
        print('*' * 62)

    def loop(self):
        """Игровой цикл"""
        num = 0
        while True:
            self.print_field()                      # печатает поля
            if num % 2 == 0:                        # определяет, чей ход
                repeat = self.us.move()             # ход пользователя
            else:
                sleep(2)                            # имитация размышления ИИ
                repeat = self.ai.move(comp=True)    # ход ИИ
            if repeat:
                num -= 1
            if self.ai.board.count == 7:            # проверка счетчика убитых кораблей
                self.print_field()                  # печать полей после завершения игры
                print("=" * 62)
                print(f"{' ' * 21}Пользователь выиграл!")
                break

            if self.us.board.count == 7:            # проверка счетчика убитых кораблей
                self.print_field()                  # печать полей после завершения игры
                print("=" * 62)
                print(f"{' ' * 23}Компьютер выиграл!")
                break
            num += 1

    def start(self):
        """Старт игры"""
        self.greet()
        self.loop()


g = Game()
g.start()
