# -*-coding:utf8-*-
'''
通过ADB将andriod指令发送到手机上，操作物联家APP完成公文的自动处理
Created on 3-14-2018
@author: Chen Yongji
'''

import os
import sys
import platform
import time
import re
from PIL import Image


def isConnect():
    devices = os.popen('adb devices').readlines()[1]
    if 'device' in devices:
        return True
    else:
        print('找不到手机！请连接手机，并确保调试模式正常打开！')
        exit()


def screenshot():
    path = os.path.split(os.path.realpath(__file__))
    fp = path[0]
    os.system('adb shell screencap -p /storage/emulated/0/temp.png')
    os.system('adb pull /storage/emulated/0/temp.png "' + fp + '"')


# 对首条公文标题位置截取，并进行二值化处理，存在黑色像素点，返回true
def imgCheck(checkPosition):
	img = Image.open('./temp.png')
	img = img.transform((70,20), Image.EXTENT,checkPosition).convert('1')
	imgList = list(img.tobytes())
	for i in range(0,len(imgList)):
		if imgList[i] < 100:
			return True
	return False


def getResolution(image):
    img = Image.open(image)
    width, heigh = img.size
    return width, heigh


def isScreenLocked():
    OS = list(platform.uname())[0]
    if OS == 'Windows':
        filterCommand = 'findstr'
    else:
        filterCommand = 'grep'
    adbResult = os.popen('adb shell dumpsys window policy | ' + filterCommand + ' Lockscreen=')
    isScreenLocked = list(adbResult)[0].split()[1].split('=')[1]
    return isScreenLocked


def autoClick():
    iniLineList = []
    count = 0
 
    time.sleep(1)
    screenshot()       
    width, heigh = getResolution('temp.png')
    with open('clickPoint.ini', 'r') as ini:
        for line in ini.readlines():
            iniLineList.extend(line.strip().split(' '))
        for i in range(0, len(iniLineList), 3):
            if str(width) in iniLineList[i] and str(heigh) in iniLineList[i]:
                checkPosition = iniLineList[i+1]
                tapPosition = re.split(':|,', iniLineList[i+2])
                # 需要对坐标配置文件里的公文标题位置坐标转化为元组，再传入imgCheck()进行是否需要继续处理公文判断
                while imgCheck(tuple(eval(checkPosition))):
                    # 按键位置坐标列表，偶数位为X坐标，奇数位为Y坐标                   
                    for t in range(0,len(tapPosition),2):
                        os.system('adb shell input touchscreen tap '+ tapPosition[t] +' '+ tapPosition[t+1] +'')
                        # 等待服务器侧响应
                        time.sleep(2)
                    # 等待服务器侧响应
                    time.sleep(3)
                    #os.system('adb shell input keyevent 4')
                    count += 1
                    print('处理完成' + str(count) + '个公文！')
                    screenshot()
            else:
                print('当前手机屏幕分辨率的键位配置不存在！')
                exit()


def main():
    if isConnect():
        if isScreenLocked() == str('true'):
            print('请先解锁手机屏幕')
            exit()
        else:
            startResult = list(os.popen('adb shell am start -n com.cmiot.oa/com.cmiot.oa.MainActivity'))
            if len(startResult) != 1:
                print('物联家APP启动失败或已启动！')
                exit()
            else:
                time.sleep(2)
                os.system('adb shell input touchscreen tap 125 425')
                autoClick()
    os.remove('temp.png')
    os.system('adb shell rm /storage/emulated/0/temp.png')


if __name__ == '__main__':
    main()
