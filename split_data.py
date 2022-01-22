import os
import random
import shutil


xmlfilepath = '/home/why/DL/ConditionalDETR-main/data/Annotations'
jpgfilepath = '/home/why/DL/ConditionalDETR-main/data/JPEGImages'
# txtsavepath = 'ImageSets\Main'
total_xml = os.listdir(xmlfilepath)
# print (total_xml)
num = len(total_xml)
# list = range(num)
# tv = int(num * trainval_percent)
# tr = int(tv * train_percent)
# trainval = random.sample(num, tv)#从list中随机获取tv个元素，作为一个片断返回
train = random.sample(total_xml, k=int(num*0.7))
val = [i for i in train]
a = len(train)
i = 0
for xml in total_xml:
    jpg_name = xml.replace(xml.split(".")[-1], "jpg")
    if xml in train:
        i+=1
        shutil.copy(os.path.join(xmlfilepath,xml),"/home/why/DL/ConditionalDETR-main/ship1/annotations/train2017")
        shutil.copy(os.path.join(jpgfilepath, jpg_name), "/home/why/DL/ConditionalDETR-main/ship1/images/train2017")
    else:
        shutil.copy(os.path.join(xmlfilepath, xml), "/home/why/DL/ConditionalDETR-main/ship1/annotations/val2017")
        shutil.copy(os.path.join(jpgfilepath, jpg_name), "/home/why/DL/ConditionalDETR-main/ship1/images/val2017")
print(i)

# val = [i for i in total_xml ]
# train = random.sample(trainval, tr)
# print(train)

# ftrainval = open('ImageSets/Main/trainval.txt', 'w')
# print (ftrainval)
# ftest = open('ImageSets/Main/test.txt', 'w')
# ftrain = open('ImageSets/Main/train.txt', 'w')
# fval = open('ImageSets/Main/val.txt', 'w')
#
# for i in list:
#     name = total_xml[i][:-4] + '\n'#也就是去除‘.xml’这四个字符
#
#
#     if i in trainval:
#         ftrainval.write(name)
#         if i in train:
#             ftest.write(name)
#         else:
#             fval.write(name)
#     else:
#         ftrain.write(name)
#
# ftrainval.close()
# ftrain.close()
# fval.close()
# ftest.close()
