#coding: utf-8
import re
import os

def sign(x):
    if x < 0:
        return -1
    else:
        return 1

class Corrector:
    """ MODE depends on TCN file section.
        Can be: None, SIDE_1..."""
    def __init__(self):
        self.L, self.W, self.S = None, None, None
        self.ADDITIONAL_DEEP = 6
        self.MODE = None
        self.line = ""

    def parse_header(self, line):
        p = re.compile(r"::UNm DL=(?P<L>\d+\.?\d*) DH=(?P<W>\d+\.?\d*) DS=(?P<S>\d+\.?\d*)")
        m = p.match(line)
        if m:
            self.L, self.W, self.S = m.groups()
            return 0
        else:
            raise Exception("Заголовок не распознан")
            return -1
    
    def if_header_parsed(method):
        def wrapper(self, line):
            if self.S:
                return method(self, line)
            else:
                return line
        return wrapper
    
    @if_header_parsed
    def correct_deep(self, line):
        deep, diameter = 0, 0

        p_deep = re.compile(r"#3=(?P<deep>-?\d+\.?\d*)")
        m_deep = p_deep.search(line)
        if m_deep:
            deep = m_deep.group("deep")
        else:
            return line
        p_diameter = re.compile(r"#1002=(?P<diameter>\d+\.?\d*)")
        m_diameter = p_diameter.search(line)
        if m_diameter:
            diameter = m_diameter.group("diameter")
        else:
            return line
        
        if int(diameter) not in (5, 8, 10, 15, 20, 35):
            line = line.replace("#1002={}".format(diameter), "#1002=8")
            line = line.replace("#1001=0", "#1001=1")
            line = line.replace("#3={}".format(deep), "#3=-1")
            return line
        elif self.MODE == "SIDE_1" and deep == self.S:
            return line.replace("#3=-{}".format(deep), ("#3=-{}".format(float(deep) + 7)))
        elif (self.MODE in ("SIDE_2", "SIDE_3", "SIDE_4", "SIDE_5", "SIDE_6")
              and abs(float(deep)) > 33):
            return line.replace("#3={}".format(deep), ("#3={}".format(33 * sign(float(deep)))))
        else:
            return line
    
    @if_header_parsed
    def correct_base(self, line):
        p = re.compile(r"#1=(?P<coord>\d+\.?\d*)")
        m = p.search(line)
        if m:
            coord = m.group("coord")
            if float(coord) > float(self.L) / 2:
                _line = line.replace("#1={}".format(coord), "#1=lf-{}".format(float(self.L) - float(coord)))
                _line = _line.replace("WS=", "WO=1 WS")
                return _line
        return line

def main():
    cor = Corrector()
    try:
        os.mkdir(os.getcwd() + "/_")
    except FileExistsError:
        pass
    #try:
    for root, dirs, files in os.walk(os.getcwd()):
        if root == os.getcwd() + os.path.normpath("/_"):
            continue
        for _file in files:
            if _file.lower().endswith(".tcn"):
                with open(_file) as f,\
                    open('_/_' + _file, 'w') as nf:
                    cnt = 0

                    for line in f:
                        cnt += 1
                        if cnt == 3:
                            cor.parse_header(line)

                        if line == "SIDE#1{\n":
                            cor.MODE = "SIDE_1"
                        elif line == "SIDE#2{\n":
                            cor.MODE = "SIDE_2"
                        elif line == "SIDE#3{\n":
                            cor.MODE = "SIDE_3"
                        elif line == "SIDE#4{\n":
                            cor.MODE = "SIDE_4"
                        elif line == "SIDE#5{\n":
                            cor.MODE = "SIDE_5"
                        elif line == "SIDE#6{\n":
                            cor.MODE = "SIDE_6"

                        _line = cor.correct_deep(line)
                        _line = cor.correct_base(_line)

                        nf.write(_line)
    # except Exception as ex:
    #     print("Ошибка: " + str(ex))
    #     input("Нажмите любую клавишу для выхода.")
    #     raise ex
    #     return
    print("Обработка завершена без ошибок.")
    input("Нажмите любую клавишу, чтобы закрыть это окно.")

if __name__ == '__main__':
    main()