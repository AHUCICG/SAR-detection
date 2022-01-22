# #!/usr/bin/python
#
# #pip install lxml
#!/usr/bin/python

# pip install lxml

import sys
import os
import json
import xml.etree.ElementTree as ET
import glob

START_BOUNDING_BOX_ID = 1
#PRE_DEFINE_CATEGORIES = None


#If necessary, pre-define category and its id
PRE_DEFINE_CATEGORIES = {"ship": 0}


def get(root, name):
    vars = root.findall(name)
    return vars


def get_and_check(root, name, length):
    vars = root.findall(name)
    if len(vars) == 0:
        raise ValueError("Can not find %s in %s." % (name, root.tag))
    if length > 0 and len(vars) != length:
        raise ValueError(
            "The size of %s is supposed to be %d, but is %d."
            % (name, length, len(vars))
        )
    if length == 1:
        vars = vars[0]
    return vars


def get_filename_as_int(filename):
    try:
        filename = filename.replace("\\", "/")
        filename = os.path.splitext(os.path.basename(filename))[0]
        return int(filename) #文件名改成字符串
    except:
        raise ValueError("Filename %s is supposed to be an integer." % (filename))


def get_categories(xml_files):
    """Generate category name to id mapping from a list of xml files.

    Arguments:
        xml_files {list} -- A list of xml file paths.

    Returns:
        dict -- category name to id mapping.
    """
    classes_names = []
    for xml_file in xml_files:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        for member in root.findall("object"):
            classes_names.append(member[0].text)
    classes_names = list(set(classes_names))
    classes_names.sort()
    return {name: i for i, name in enumerate(classes_names)}


def convert(xml_files, json_file):
    json_dict = {"images": [], "type": "instances", "annotations": [], "categories": []}
    if PRE_DEFINE_CATEGORIES is not None:
        categories = PRE_DEFINE_CATEGORIES
    else:
        categories = get_categories(xml_files)
    bnd_id = START_BOUNDING_BOX_ID
    for xml_file in xml_files:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        path = get(root, "path")
        if len(path) == 1:
            filename = os.path.basename(path[0].text)
        elif len(path) == 0:
            filename = get_and_check(root, "filename", 1).text
        else:
            raise ValueError("%d paths found in %s" % (len(path), xml_file))
        ## The filename must be a number
       # image_id = get_filename_as_int(filename)
        img_name = os.path.basename(filename)[:-1]
        image_id = os.path.splitext(img_name)[0]
        size = get_and_check(root, "size", 1)
        width = int(get_and_check(size, "width", 1).text)
        height = int(get_and_check(size, "height", 1).text)
        image = {
            "file_name": filename,
            "height": height,
            "width": width,
            "id": image_id,
        }
        json_dict["images"].append(image)
        ## Currently we do not support segmentation.
        #  segmented = get_and_check(root, 'segmented', 1).text
        #  assert segmented == '0'
        for obj in get(root, "object"):
            category = get_and_check(obj, "name", 1).text
            if category not in categories:
                new_id = len(categories)
                categories[category] = new_id
            category_id = categories[category]
            bndbox = get_and_check(obj, "bndbox", 1)
            xmin = int(get_and_check(bndbox, "xmin", 1).text) - 1
            ymin = int(get_and_check(bndbox, "ymin", 1).text) - 1
            xmax = int(get_and_check(bndbox, "xmax", 1).text)
            ymax = int(get_and_check(bndbox, "ymax", 1).text)
            assert xmax > xmin
            assert ymax > ymin
            o_width = abs(xmax - xmin)
            o_height = abs(ymax - ymin)
            ann = {
                "area": o_width * o_height,
                "iscrowd": 0,
                "image_id": image_id,
                "bbox": [xmin, ymin, o_width, o_height],
                "category_id": category_id,
                "id": bnd_id,
                "ignore": 0,
                "segmentation": [],
            }
            json_dict["annotations"].append(ann)
            bnd_id = bnd_id + 1

    for cate, cid in categories.items():
        cat = {"supercategory": "none", "id": cid, "name": cate}
        json_dict["categories"].append(cat)

    os.makedirs(os.path.dirname(json_file), exist_ok=True)
    json_fp = open(json_file, "w")
    json_str = json.dumps(json_dict)
    json_fp.write(json_str)
    json_fp.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Convert Pascal VOC annotation to COCO format."
    )
    parser.add_argument("--xml_dir", help="Directory path to xml files.", type=str, default = "./Annotations")
    parser.add_argument("--json_file", help="Output COCO format json file.", type=str, default = "./instances_train2017.json")
    args = parser.parse_args()
    xml_files = glob.glob(os.path.join(args.xml_dir, "*.xml"))

    # If you want to do train/test split, you can pass a subset of xml files to convert function.
    print("Number of xml files: {}".format(len(xml_files)))
    convert(xml_files, args.json_file)
    print("Success: {}".format(args.json_file))
#
# import sys
# import os
# import json
# import xml.etree.ElementTree as ET
# import glob
#
# START_BOUNDING_BOX_ID = 1
# #PRE_DEFINE_CATEGORIES = None
#
#
# #If necessary, pre-define category and its id
# # PRE_DEFINE_CATEGORIES = {'airplane':0, 'airport':1, 'baseballfield':2, 'basketballcourt':3, 'bridge':4, 'chimney':5, 'dam':6,
# #                'Expressway-Service-area':7, 'Expressway-toll-station':8, 'golffield':9, 'groundtrackfield':10, 'harbor':11,
# #               'overpass':12, 'ship':13, 'stadium':14, 'storagetank':15, 'tenniscourt':16, 'trainstation':17, 'vehicle':18, 'windmill':19}
# PRE_DEFINE_CATEGORIES = {'ship':0,}
#
# def get(root, name):
#     vars = root.findall(name)
#     return vars
#
#
# def get_and_check(root, name, length):
#     vars = root.findall(name)
#     if len(vars) == 0:
#         raise ValueError("Can not find %s in %s." % (name, root.tag))
#     if length > 0 and len(vars) != length:
#         raise ValueError(
#             "The size of %s is supposed to be %d, but is %d."
#             % (name, length, len(vars))
#         )
#     if length == 1:
#         vars = vars[0]
#     return vars
#
#
# def get_filename_as_int(filename):
#     try:
#         filename = filename.replace("\\", "/")
#         filename = os.path.splitext(os.path.basename(filename))[0]
#         return int(filename)
#     except:
#         raise ValueError("Filename %s is supposed to be an integer." % (filename))
#
#
# def get_categories(xml_files):
#     """Generate category name to id mapping from a list of xml files.
#
#     Arguments:
#         xml_files {list} -- A list of xml file paths.
#
#     Returns:
#         dict -- category name to id mapping.
#     """
#     classes_names = []
#     for xml_file in xml_files:
#         tree = ET.parse(xml_file)
#         root = tree.getroot()
#         for member in root.findall("object"):
#             classes_names.append(member[0].text)
#     classes_names = list(set(classes_names))
#     classes_names.sort()
#     return {name: i for i, name in enumerate(classes_names)}
#
#
# def convert(xml_files, json_file):
#     json_dict = {"images": [], "type": "instances", "annotations": [], "categories": []}
#     if PRE_DEFINE_CATEGORIES is not None:
#         categories = PRE_DEFINE_CATEGORIES
#     else:
#         categories = get_categories(xml_files)
#     bnd_id = START_BOUNDING_BOX_ID
#     for xml_file in xml_files:
#         tree = ET.parse(xml_file)
#         root = tree.getroot()
#         path = get(root, "path")
#         if len(path) == 1:
#             filename = os.path.basename(path[0].text)
#         elif len(path) == 0:
#             filename = get_and_check(root, "filename", 1).text
#         else:
#             raise ValueError("%d paths found in %s" % (len(path), xml_file))
#         ## The filename must be a number
#         image_id = get_filename_as_int(filename)
#         size = get_and_check(root, "size", 1)
#         width = int(get_and_check(size, "width", 1).text)
#         height = int(get_and_check(size, "height", 1).text)
#         image = {
#             "file_name": filename,
#             "height": height,
#             "width": width,
#             "id": image_id,
#         }
#         json_dict["images"].append(image)
#         ## Currently we do not support segmentation.
#         #  segmented = get_and_check(root, 'segmented', 1).text
#         #  assert segmented == '0'
#         for obj in get(root, "object"):
#             category = get_and_check(obj, "name", 1).text
#             if category not in categories:
#                 new_id = len(categories)
#                 categories[category] = new_id
#             category_id = categories[category]
#             bndbox = get_and_check(obj, "bndbox", 1)
#             xmin = int(get_and_check(bndbox, "xmin", 1).text) - 1
#             ymin = int(get_and_check(bndbox, "ymin", 1).text) - 1
#             xmax = int(get_and_check(bndbox, "xmax", 1).text)
#             ymax = int(get_and_check(bndbox, "ymax", 1).text)
#             assert xmax > xmin
#             assert ymax > ymin
#             o_width = abs(xmax - xmin)
#             o_height = abs(ymax - ymin)
#             ann = {
#                 "area": o_width * o_height,
#                 "iscrowd": 0,
#                 "image_id": image_id,
#                 "bbox": [xmin, ymin, o_width, o_height],
#                 "category_id": category_id,
#                 "id": bnd_id,
#                 "ignore": 0,
#                 "segmentation": [],
#             }
#             json_dict["annotations"].append(ann)
#             bnd_id = bnd_id + 1
#
#     for cate, cid in categories.items():
#         cat = {"supercategory": "none", "id": cid, "name": cate}
#         json_dict["categories"].append(cat)
#
#     os.makedirs(os.path.dirname(json_file), exist_ok=True)
#     json_fp = open(json_file, "w")
#     json_str = json.dumps(json_dict)
#     json_fp.write(json_str)
#     json_fp.close()
#
#
# if __name__ == "__main__":
#     import argparse
#
#     parser = argparse.ArgumentParser(
#         description="Convert Pascal VOC annotation to COCO format."
#     )
#     parser.add_argument("--xml_dir", help="Directory path to xml files.", type=str, default = r"./Annotations")
#     parser.add_argument("--json_file", help="Output COCO format json file.", type=str, default = "./instances_train2017.json")
#     args = parser.parse_args()
#     xml_files = glob.glob(os.path.join(args.xml_dir, "*.xml"))
#
#     # If you want to do train/test split, you can pass a subset of xml files to convert function.
#     print("Number of xml files: {}".format(len(xml_files)))
#     convert(xml_files, args.json_file)
#     print("Success: {}".format(args.json_file))
#
#
# # import os
# # import cv2
# # from tqdm import tqdm
# # import json
# # import xml.dom.minidom
# #
# # category_list = ['airplane', 'airport', 'baseballfield', 'basketballcourt', 'bridge', 'chimney', 'dam',
# #               'Expressway-Service-area', 'Expressway-toll-station', 'golffield', 'groundtrackfield', 'harbor',
# #               'overpass', 'ship', 'stadium', 'storagetank', 'tenniscourt', 'trainstation', 'vehicle', 'windmill']
# #
# #
# # def convert_to_cocodetection(dir, output_dir):
# #     """
# #     input:
# #         dir:the path to DIOR dataset
# #         output_dir:the path write the coco form json file
# #     """
# #     annotations_path = dir
# #     namelist_path = os.path.join(dir, "Main")
# #     trainval_images_path = os.path.join(dir, "JPEGImages-trainval")
# #     test_images_path = os.path.join(dir, "JPEGImages-test")
# #     id_num = 0
# #     categories = [{"id": 0, "name": "Airplane"},
# #                   {"id": 1, "name": "Airport"},
# #                   {"id": 2, "name": "Baseball field"},
# #                   {"id": 3, "name": "Basketball court"},
# #                   {"id": 4, "name": "Bridge"},
# #                   {"id": 5, "name": "Chimney"},
# #                   {"id": 6, "name": "Dam"},
# #                   {"id": 7, "name": "Expressway service area"},
# #                   {"id": 8, "name": "Expressway toll station"},
# #                   {"id": 9, "name": "Golf course"},
# #                   {"id": 10, "name": "Ground track field"},
# #                   {"id": 11, "name": "Harbor"},
# #                   {"id": 12, "name": "Overpass"},
# #                   {"id": 13, "name": "Ship"},
# #                   {"id": 14, "name": "Stadium"},
# #                   {"id": 15, "name": "Storage tank"},
# #                   {"id": 16, "name": "Tennis court"},
# #                   {"id": 17, "name": "Train station"},
# #                   {"id": 18, "name": "Vehicle"},
# #                   {"id": 19, "name": "Wind mill"},
# #                   ]
# #     for mode in ["train", "val"]:
# #         images = []
# #         annotations = []
# #         print(f"start loading {mode} data...")
# #         if mode == "train":
# #             f = open(namelist_path + "/" + "train.txt", "r")
# #             images_path = trainval_images_path
# #         else:
# #             f = open(namelist_path + "/" + "val.txt", "r")
# #             images_path = trainval_images_path
# #         for name in tqdm(f.readlines()):
# #             # image part
# #             image = {}
# #
# #             name = name.replace("\n", "")
# #             image_name = name + ".jpg"
# #             annotation_name = name + ".xml"
# #             height, width = cv2.imread(images_path + "/" + image_name).shape[:2]
# #             image["file_name"] = image_name
# #             image["height"] = height
# #             image["width"] = width
# #             image["id"] = name
# #             images.append(image)
# #             # anno part
# #             dom = xml.dom.minidom.parse(dir + "/" + annotation_name)
# #             root_data = dom.documentElement
# #             for i in range(len(root_data.getElementsByTagName('name'))):
# #                 annotation = {}
# #                 category = root_data.getElementsByTagName('name')[i].firstChild.data
# #                 top_left_x = root_data.getElementsByTagName('xmin')[i].firstChild.data
# #                 top_left_y = root_data.getElementsByTagName('ymin')[i].firstChild.data
# #                 right_bottom_x = root_data.getElementsByTagName('xmax')[i].firstChild.data
# #                 right_bottom_y = root_data.getElementsByTagName('ymax')[i].firstChild.data
# #                 bbox = [top_left_x, top_left_y, right_bottom_x, right_bottom_y]
# #                 bbox = [int(i) for i in bbox]
# #                 bbox = xyxy_to_xywh(bbox)
# #                 annotation["image_id"] = name
# #                 annotation["bbox"] = bbox
# #                 annotation["category_id"] = category_list.index(category)
# #                 annotation["id"] = id_num
# #                 annotation["iscrowd"] = 0
# #                 annotation["segmentation"] = []
# #                 annotation["area"] = bbox[2] * bbox[3]
# #                 id_num += 1
# #                 annotations.append(annotation)
# #         dataset_dict = {}
# #         dataset_dict["images"] = images
# #         dataset_dict["annotations"] = annotations
# #         dataset_dict["categories"] = categories
# #         json_str = json.dumps(dataset_dict)
# #         with open(f'{output_dir}/DIOR_{mode}_coco.json', 'w') as json_file:
# #             json_file.write(json_str)
# #     print("json file write done...")
# #
# #
# # def get_test_namelist(dir, out_dir):
# #     full_path = out_dir + "/" + "test.txt"
# #     file = open(full_path, 'w')
# #     for name in tqdm(os.listdir(dir)):
# #         name = name.replace(".txt", "")
# #         file.write(name + "\n")
# #     file.close()
# #     return None
# #
# #
# # def centerxywh_to_xyxy(boxes):
# #     """
# #     args:
# #         boxes:list of center_x,center_y,width,height,
# #     return:
# #         boxes:list of x,y,x,y,cooresponding to top left and bottom right
# #     """
# #     x_top_left = boxes[0] - boxes[2] / 2
# #     y_top_left = boxes[1] - boxes[3] / 2
# #     x_bottom_right = boxes[0] + boxes[2] / 2
# #     y_bottom_right = boxes[1] + boxes[3] / 2
# #     return [x_top_left, y_top_left, x_bottom_right, y_bottom_right]
# #
# #
# # def centerxywh_to_topleftxywh(boxes):
# #     """
# #     args:
# #         boxes:list of center_x,center_y,width,height,
# #     return:
# #         boxes:list of x,y,x,y,cooresponding to top left and bottom right
# #     """
# #     x_top_left = boxes[0] - boxes[2] / 2
# #     y_top_left = boxes[1] - boxes[3] / 2
# #     width = boxes[2]
# #     height = boxes[3]
# #     return [x_top_left, y_top_left, width, height]
# #
# #
# # def xyxy_to_xywh(boxes):
# #     width = boxes[2] - boxes[0]
# #     height = boxes[3] - boxes[1]
# #     return [boxes[0], boxes[1], width, height]
# #
# #
# # def clamp(coord, width, height):
# #     if coord[0] < 0:
# #         coord[0] = 0
# #     if coord[1] < 0:
# #         coord[1] = 0
# #     if coord[2] > width:
# #         coord[2] = width
# #     if coord[3] > height:
# #         coord[3] = height
# #     return coord
# #
# #
# # if __name__ == '__main__':
# #     convert_to_cocodetection(r"path to your DIOR dataset", r"the path you want to write the coco format json file")
