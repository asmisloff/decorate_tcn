#coding: utf-8
import re

def match_header(line):
    p = re.compile(r"::UNm DL=(?P<L>\d+) DH=(?P<W>\d+) DS=(?P<S>\d+)")
    return p.match(line)

def main():
    path = "8_1.TCN"
    cnt = 0
    with open(path) as f,\
         open('_' + path, 'w') as nf:
        L, W, S, through_hole = None, None, None, None
        cnt = 0
        for line in f:
            cnt += 1
            if (cnt == 3):
                m = match_header(line)
                if m:
                    L, W, S = m.groups()
                    through_hole = "#3=-{}".format(S)
            
            if S:
                nf.write(line.replace(through_hole, ("#3=-{}".format(int(S) + 5))))
            else:
                nf.write(line)

if __name__ == '__main__':
    main()