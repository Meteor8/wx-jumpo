import os
import time
import random
from PIL import Image, ImageDraw


class Funx(object):
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img

    def brightness(self):
        R = self.img[self.x, self.y][0]
        G = self.img[self.x, self.y][1]
        B = self.img[self.x, self.y][2]
        # Brightness = 0.3 * R + 0.6 * G + 0.1 * B，用整数替代，避免用浮点数降低速度
        return 3 * R + 6 * G + 1 * B

    def aberration(self):  # 色差函数1，用于计算像素与其上方像素的色差值(自定义为RGB三色平方和)，用于确认边缘
        return (self.img[self.x, self.y][0] - self.img[self.x, self.y - 1][0]) ** 2 + (self.img[self.x, self.y][1] -
                                                                                       self.img[self.x, self.y - 1][1]) ** 2 + (self.img[self.x, self.y][2] - self.img[self.x, self.y - 1][2]) ** 2

    def abercompare(self, a, b):  # 色差函数2，用于计算像素与另一像素的色差值，用于确认快速找色块
        return (self.img[self.x, self.y][0] - self.img[a, b][0]) ** 2 + (self.img[self.x, self.y]
                                                                         [1] - self.img[a, b][1]) ** 2 + (self.img[self.x, self.y][2] - self.img[a, b][2]) ** 2

    def aber(self, rgb):  # 色差函数3，用于计算像素与某一RGB颜色的色差值，用于确认特定颜色
        return (self.img[self.x, self.y][0] - rgb[0]) ** 2 + (self.img[self.x, self.y]
                                                              [1] - rgb[1]) ** 2 + (self.img[self.x, self.y][2] - rgb[2]) ** 2


def get_image(filename):
    os.system('adb shell screencap ' + phonePath + filename)
    os.system('adb pull ' + phonePath + filename + " " + pcPath + filename)
    os.system('adb shell rm ' + phonePath + filename)


def search_starter(filename, start, stepy, stepx):  # 快速查找起始点，以便后续逐行扫描
    if stepy > 3 and stepx > 3:
        img = Image.open(pcPath + filename).load()
        for y in range(start, resolutiony, stepy):  # 粗略查找物体位置，默认行间隔50，列间隔30
            for x in range(0, resolutionx, stepx):
                funx = Funx(x, y, img)
                if funx.abercompare(resolutionx - 1, resolutiony //
                                    2) > 400 and y - stepy >= max(resolutiony // 4, start):
                    nextstart = y - stepy
                    return search_starter(
                        filename, nextstart, stepy // 2, stepx // 2)
        return start
    else:
        return start


def get_point(filename, start):
    img = Image.open(pcPath + filename).load()
    chessman_x = chessman_y = counter_man = 0  # 棋子x,y,像素数
    chessboard_x = chessboard_y = counter_board = 0  # 棋盘x,y,像素数,
    for y in range(start, resolutiony):
        if counter_man > 0 and y > chessman_y and counter_board > 0 and y > chessboard_y:  # 一旦棋子和棋盘都找到，则结束循环
            break
        for x in range(resolutionx):
            funx = Funx(x, y, img)
            if counter_man == 0 or y <= chessman_y:  # 找到棋子后,此行查找完即结束棋子查找
                if 550 > funx.brightness() > 520 and funx.aber((52, 53, 60)) < 40 and funx.aberration(
                ) > 300:  # 认为亮度在[520,550)之间,且竖直色差大于50000的，属于棋子的像素（注意：咖啡杯顶部有一个像素亮度刚好为550，故550取闭）
                    if counter_man == 0:
                        chessman_x = x
                        chessman_y = y  # 一旦找到第一个位置，chessman_y > 0后，对棋子的搜索即结束
                    counter_man += 1
            if counter_board == 0 or y <= chessboard_y:
                if counter_man > 0:  # 但棋子比棋盘先找到时，意味着棋盘离棋子很近，此时寻找棋盘的像素需要消除棋子像素的干扰
                    if funx.brightness() > 600 and funx.aberration() > 500 and funx.aber((52, 53, 60)
                                                                                         ) > 100 and abs(x - chessman_x) > 100:  # 认为满足亮度大于棋子，色差大于1000的第一个点，属于棋盘的像素
                        if counter_board == 0:
                            chessboard_x = x
                            chessboard_y = y  # 一旦找到第一个位置，chessboard_y > 0后，对棋盘的搜索即结束
                        counter_board += 1
                else:
                    if funx.brightness() > 600 and funx.aberration() > 500:
                        if counter_board == 0:
                            chessboard_x = x
                            chessboard_y = y  # 一旦找到第一个位置，chessboard_y > 0后，对棋盘的搜索即结束
                        counter_board += 1
    return chessman_x + counter_man // 2, chessman_y, chessboard_x + \
        counter_board // 2, chessboard_y


def time_calc(filename):
    image = Image.open(pcPath + filename)
    starter = search_starter(filename, resolutiony // 4, 50, 30)
    man_x, man_y, board_x, board_y = get_point(filename, starter)
    print('棋子：({},{})棋盘：({},{})'.format(man_x, man_y, board_x, board_y))

    distance = abs(man_x - board_x)
    calctime = distance / initdistance * inittime
    if abs(man_x - board_x) < 10:
        calctime = 400

    # 画图用于调试，可注释掉
    draw = ImageDraw.Draw(image)
    draw.line((man_x, 0, man_x, resolutiony), fill='yellow')
    draw.line((0, man_y, resolutionx, man_y), fill='yellow')
    draw.line((board_x, 0, board_x, resolutiony), fill='black')
    draw.line((0, board_y, resolutionx, board_y), fill='black')
    image.save(pcPath + filename)
    ########

    image.close()
    return round(calctime)


def tap_it(swipetime):
    touch_area = random.randint(300, 350)
    sleeptime = random.uniform(1.0, 2.0)
    os.system('adb shell input swipe {} {} {} {} {}'.format(
        touch_area, touch_area, touch_area, touch_area, swipetime))
    time.sleep(sleeptime)


phonePath = '/storage/emulated/0/test/'  # 手机截图临时存储路径
pcPath = 'E:/Project001/jumpo/'  # 图片电脑端存储路径
initdistance = 591 - 251  # 第一步的距离，可先运行后再修改
inittime = 731  # 跳跃△x距离需要的按压时间,用于度量，与分辨率无关
expected_score = 10  # 目标运行步数
resolutionx, resolutiony = 810, 1440  # 手机分辨率
for i in range(1, expected_score + 1):
    myfilename = '{}.png'.format(i)
    get_image(myfilename)
    mytime = time_calc(myfilename)
    tap_it(mytime)
