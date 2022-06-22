import sys
import functools
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt


class Calculator:
    def __init__(self):
        self.numbers = ('0', '1', '2', '3', '4',
                        '5', '6', '7', '8', '9')
        self.special_char = ('(', ')', '-', '+', '^', '\u03C0',
                             'x', '\u00F7', '\u221A', 'e', ' ', '.')
        self.exceptions = []

    def _convert_to_float(self, a):
        try:
            converted = []
            for i in a:
                converted.append(float(i))
            return converted
        except:
            self.exceptions.append('unsuccessful number conversion')
            return False

    def _add(self, a, b):
        num = self._convert_to_float([a, b])
        if not num:
            return False
        return num[0] + num[1]

    def _subtract(self, a, b):
        num = self._convert_to_float([a, b])
        if not num:
            return False
        return num[0] - num[1]

    def _multiply(self, a, b):
        num = self._convert_to_float([a, b])
        if not num:
            return False
        return num[0] * num[1]

    def _divide(self, a, b):
        num = self._convert_to_float([a, b])
        if not num:
            return False
        if num[1] == 0:
            self.exceptions.append('invalid division by 0')
            return False
        return num[0] / num[1]

    def _square_root(self, a):
        num = self._convert_to_float([a])
        if not num:
            return False
        if num[0] < 0:
            self.exceptions.append('invalid square root expression')
            return False
        return np.sqrt(num[0])

    def _power(self, a, b):
        num = self._convert_to_float([a, b])
        if not num:
            return False
        return np.power(num[0], num[1])

    def _minus(self, a):
        num = self._convert_to_float([a])
        if not num:
            return False
        return - num[0]

    def _convert_input(self, input_string, first_iteration=True):
        if not input_string:
            return False
        if first_iteration:
            left = input_string.count('(')
            right = input_string.count(')')
            if left != right:
                self.exceptions.append('invalid bracket')
                return False
        skip_count = 0
        operation_list = []
        bracket_length = np.NAN
        for i_index in range(len(input_string)):
            i = input_string[i_index]
            if skip_count > 0:
                skip_count -= 1
                continue
            if i == ' ':
                continue
            elif i in self.numbers:
                if i_index == 0 or input_string[i_index - 1] in self.special_char \
                        and input_string[i_index - 1] != '.':
                    operation_list.append(i)
                else:
                    operation_list[-1] += i
            elif i == 'e':
                if i_index == 0 or input_string[i_index - 1] in self.special_char \
                        and input_string[i_index - 1] != '.':
                    operation_list.append(np.e)
                else:
                    self.exceptions.append('invalid "e" placement')
                    operation_list = False
                    break
            elif i == '\u03C0':
                if i_index == 0 or input_string[i_index - 1] in self.special_char \
                        and input_string[i_index - 1] != '.':
                    operation_list.append(np.pi)
                else:
                    self.exceptions.append('invalid "\u03C0" placement')
                    operation_list = False
                    break
            elif i == ')':
                bracket_length = i_index + 1
                break
            elif i == '(':
                bracket, length = self._convert_input(input_string[i_index + 1:], False)
                operation_list.append(bracket)
                skip_count += length
            elif i == '+':
                if i_index != 0:
                    operation_list.append('add')
            elif i == '-':
                if len(input_string) == 1:
                    self.exceptions.append('invalid syntax placement')
                    operation_list = False
                    break
                if len(operation_list) == 0:
                    operation_list.append('minus')
                elif operation_list[-1] in self.special_char:
                    operation_list.append('minus')
                else:
                    operation_list.append('subtract')
            elif i == 'x':
                if i_index == 0:
                    self.exceptions.append('invalid syntax placement')
                    operation_list = False
                    break
                operation_list.append('multiply')
            elif i == '\u00F7':
                if i_index == 0:
                    self.exceptions.append('invalid syntax placement')
                    operation_list = False
                    break
                operation_list.append('divide')
            elif i == '\u221A':
                if len(input_string) == 1:
                    self.exceptions.append('invalid syntax placement')
                    operation_list = False
                    break
                operation_list.append('square_root')
            elif i == '.':
                if i_index == 0:
                    self.exceptions.append('invalid syntax placement')
                    operation_list = None
                    break
                if len(operation_list) > 0:
                    previous_expression = operation_list[-1]
                    invalid_placement = False
                    for j in previous_expression:
                        if j == '.' or j in self.special_char:
                            self.exceptions.append('invalid syntax placement')
                            operation_list = False
                            invalid_placement = True
                            break
                    if invalid_placement:
                        break
                    operation_list[-1] += i
            elif i == '^':
                if i_index == 0:
                    self.exceptions.append('invalid syntax placement')
                    operation_list = False
                    break
                operation_list.append('power')
            else:
                self.exceptions.append('invalid characters used')
                operation_list = False
                break

        if not operation_list:
            operation_list = False
        elif False in operation_list:
            operation_list = False
        for i_index in range(len(operation_list)):
            i = operation_list[i_index]
            if type(i) == list and i_index - 1 != len(operation_list):
                if type(operation_list[i_index + 1]) == list:
                    operation_list = False
                    break

        return operation_list, bracket_length

    @staticmethod
    def _convert_final_result(a):
        try:
            if a % 1 == 0:
                return int(a)
            return a
        except:
            return a

    def _process_input(self, expression):
        result = np.NAN
        if not expression and expression != 0:
            return 'invalid expression'
        while type(expression) == list:
            if len(expression) == 1 and type(expression[0]) != list:
                result = self._convert_final_result(expression[0])
                break
            update = False
            for i_index in range(len(expression)):
                i = expression[i_index]
                if not i and i != 0:
                    expression = False
                    update = True
                    break
                elif type(i) == list:
                    expression[i_index] = self._process_input(i)
                    update = True
                    break
            if update:
                continue
            update = False
            for i_index in range(len(expression)):
                i = expression[i_index]
                if i == 'minus':
                    expression[i_index] = self._minus(expression[i_index + 1])
                    expression.pop(i_index + 1)
                    update = True
                    break
                elif i == 'square_root':
                    expression[i_index] = self._square_root(expression[i_index + 1])
                    expression.pop(i_index + 1)
                    update = True
                    break
            if update:
                continue
            if len(expression) > 2:
                update = False
                for i_index in range(len(expression)):
                    i = expression[i_index]
                    if i == 'multiply':
                        expression[i_index - 1] = self._multiply(
                            expression[i_index - 1], expression[i_index + 1]
                        )
                        expression.pop(i_index + 1)
                        expression.pop(i_index)
                        update = True
                        break
                    elif i == 'divide':
                        expression[i_index - 1] = self._divide(
                            expression[i_index - 1], expression[i_index + 1]
                        )
                        expression.pop(i_index + 1)
                        expression.pop(i_index)
                        update = True
                        break
                    elif i == 'power':
                        expression[i_index - 1] = self._power(
                            expression[i_index - 1], expression[i_index + 1]
                        )
                        expression.pop(i_index + 1)
                        expression.pop(i_index)
                        update = True
                        break
                if update:
                    continue
            if len(expression) > 2:
                for i_index in range(len(expression)):
                    i = expression[i_index]
                    if i == 'add':
                        expression[i_index - 1] = self._add(
                            expression[i_index - 1], expression[i_index + 1]
                        )
                        expression.pop(i_index + 1)
                        expression.pop(i_index)
                        break
                    elif i == 'subtract':
                        expression[i_index - 1] = self._subtract(
                            expression[i_index - 1], expression[i_index + 1]
                        )
                        expression.pop(i_index + 1)
                        expression.pop(i_index)
                        break

        return result

    def calculate(self, input_string):
        self.exceptions = []
        expression, _ = self._convert_input(input_string)
        return self._process_input(expression), self.exceptions


class Gui(QMainWindow):
    def __init__(self, calculator):
        super().__init__()
        QApplication.processEvents()
        self.cal = calculator
        self.exceptions = []

        # main window options
        self.title = "Calculator"
        self.height = 200
        self.width = 300
        self.left = 700
        self.top = 300
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # setting up whole GUI
        self._create_layouts()
        self._create_textboxes()
        self._create_buttons()

    def _create_layouts(self):
        self.main_layout = QVBoxLayout()
        self.textboxes_layout = QVBoxLayout()
        self.buttons_layout = QGridLayout()

        self.main_layout.addLayout(self.textboxes_layout)
        self.main_layout.addLayout(self.buttons_layout)

        self._main_widget = QWidget(self)
        self.setCentralWidget(self._main_widget)
        self._main_widget.setLayout(self.main_layout)

    def _create_textboxes(self):
        self.main_textbox = QLineEdit()
        self.main_textbox.setAlignment(Qt.AlignRight)
        self.main_textbox.setReadOnly(True)
        self.main_textbox.setPlaceholderText("enter expression:")

        self.secondary_textbox = QLineEdit()
        self.secondary_textbox.setAlignment(Qt.AlignRight)
        self.secondary_textbox.setReadOnly(True)
        self.secondary_textbox.setPlaceholderText("result:")

        self.textboxes_layout.addWidget(self.main_textbox)
        self.textboxes_layout.addWidget(self.secondary_textbox)

        self.main_textbox_text = ''
        self.secondary_textbox_text = ''

    def _create_buttons(self):
        button_values = ('7', '8', '9', '\u00F7', '\u221A', 'e',  # u00F7 -> divide symbol, u221A -> square root symbol
                         '4', '5', '6', 'x', '^', 'C',
                         '1', '2', '3', '-', '.', '<-',
                         '(', '0', ')', '+', '\u03C0', '=')  # u03C0 -> pi symbol

        self.button_collection = []
        x, y, v = 0, 0, 0
        for i in button_values:
            self.button_collection.append(QPushButton(i))
            self.buttons_layout.addWidget(self.button_collection[v], x, y)
            self.button_collection[v].clicked.connect(functools.partial(self._on_button_click, i))
            v += 1
            y += 1
            if y > 5:
                y = 0
                x += 1

    def _on_button_click(self, val):
        self.main_textbox_text = self.main_textbox.text()
        self.secondary_textbox_text = self.secondary_textbox.text()

        if self.secondary_textbox_text != '' or val != '=':
            self.secondary_textbox_text = ''

        if val in self.cal.special_char or val in self.cal.numbers:
            self.main_textbox_text += val
        elif val == '<-':
            if len(self.main_textbox_text) > 0:
                self.main_textbox_text = self.main_textbox_text[
                                         0:len(self.main_textbox_text) - 1]
        elif val == 'C':
            self.main_textbox_text = ''
        elif val == '=':
            self.secondary_textbox_text, self.exceptions = self.cal.calculate(
                self.main_textbox_text
            )

        if len(self.exceptions) > 0:
            self._exception_box()
            self.exceptions = []
            self.secondary_textbox_text = 'invalid expression'
        self.main_textbox.setText(self.main_textbox_text)
        self.secondary_textbox.setText(str(self.secondary_textbox_text))

    def _exception_box(self):
        e = QMessageBox()
        e.setIcon(QMessageBox.Warning)
        exceptions = 'Some exceptions occurred:'
        for i in self.exceptions:
            exceptions += '\n- ' + i
        e.setText(exceptions)
        e.setWindowTitle("Exception")
        e.setStandardButtons(QMessageBox.Ok)
        e.exec_()


def main():
    generator = QApplication(sys.argv)
    cal = Calculator()
    gui = Gui(cal)
    gui.show()
    sys.exit(generator.exec_())


if __name__ == '__main__':
    main()
