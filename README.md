#微信跳一跳脚本
根据开源代码修改

#开始前需要准备
1.Android sdk, adb
2.ptyhon3 + pillow库

#初始化
修改以下内容
1.phonePath = '/storage/emulated/0/test/'  # 手机截图临时存储路径
2.pcPath = 'E:/Project001/jumpo/'  # 图片电脑端存储路径
3.initdistance = 591 - 251  # 第一步的距离（先运行一次后根据第一步的输出再修改）
4.resolutionx, resolutiony = 810, 1440  # 手机分辨率