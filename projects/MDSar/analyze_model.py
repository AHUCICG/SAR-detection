# -*- coding: utf-8 -*-
# Copyright (c) Facebook, Inc. and its affiliates.

import logging
import numpy as np
from collections import Counter
import tqdm
from detectron2.data.datasets import register_coco_instances
from detectron2.checkpoint import DetectionCheckpointer
from detectron2.config import get_cfg
from detectron2.data import build_detection_test_loader
from detectron2.engine import default_argument_parser,default_setup
from detectron2.modeling import build_model
from detectron2.utils.analysis import (
    activation_count_operators,
    flop_count_operators,
    parameter_count_table,
)
from detectron2.utils.logger import setup_logger
from centernet.config import add_centernet_config
logger = logging.getLogger("detectron2")

def setup(args):
    register_coco_instances("train", {}, "datasets/coco/annotations/instances_train2017.json","datasets/coco/train2017")

    register_coco_instances("test", {}, "datasets/coco/annotations/instances_val2017.json", "datasets/coco/val2017")

    cfg = get_cfg()

    add_centernet_config(cfg)
    cfg.merge_from_file(args.config_file)
    cfg.merge_from_list(args.opts)

    cfg.DATASETS.TRAIN = ("train",)
    cfg.DATASETS.TEST = ("test",)
    cfg.MODEL.CENTERNET.NUM_CLASSES = 1
    cfg.MODEL.ROI_HEADS.NUM_CLASSES = 1
    cfg.freeze()
    default_setup(cfg, args)
    return cfg


def do_flop(cfg):
    data_loader = build_detection_test_loader(cfg, cfg.DATASETS.TEST[0])
    model = build_model(cfg)
    DetectionCheckpointer(model).load(cfg.MODEL.WEIGHTS)
    model.eval()

    counts = Counter()
    total_flops = []
    for idx, data in zip(tqdm.trange(args.num_inputs), data_loader):  # noqa
        count = flop_count_operators(model, data)
        counts += count
        total_flops.append(sum(count.values()))
    logger.info(
        "(G)Flops for Each Type of Operators:\n" + str([(k, v / idx) for k, v in counts.items()])
    )
    logger.info("Total (G)Flops: {}±{}".format(np.mean(total_flops), np.std(total_flops)))


def do_activation(cfg):
    data_loader = build_detection_test_loader(cfg, cfg.DATASETS.TEST[0])
    model = build_model(cfg)
    DetectionCheckpointer(model).load(cfg.MODEL.WEIGHTS)
    model.eval()

    counts = Counter()
    total_activations = []
    for idx, data in zip(tqdm.trange(args.num_inputs), data_loader):  # noqa
        count = activation_count_operators(model, data)
        counts += count
        total_activations.append(sum(count.values()))
    logger.info(
        "(Million) Activations for Each Type of Operators:\n"
        + str([(k, v / idx) for k, v in counts.items()])
    )
    logger.info(
        "Total (Million) Activations: {}±{}".format(
            np.mean(total_activations), np.std(total_activations)
        )
    )


def do_parameter(cfg):
    model = build_model(cfg)
    logger.info("Parameter Count:\n" + parameter_count_table(model, max_depth=5))


def do_structure(cfg):
    model = build_model(cfg)
    logger.info("Model Structure:\n" + str(model))


if __name__ == "__main__":
    parser = default_argument_parser(
        epilog="""
Examples:

To show parameters of a model:
$ ./analyze_model.py --tasks parameter  --config-file ../configs/COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_1x.yaml
 ./analyze_model.py --tasks parameter  --config-file ../configs/COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_1x.yaml
 python analyze_model.py --tasks parameter --config-file ../projects/CenterNet2/configs/CenterNet2_v19_slim_FPN.yaml.yaml
Flops and activations are data-dependent, therefore inputs and model weights
are needed to count them:

$ ./analyze_model.py --num-inputs 100 --tasks flop \\
    --config-file ../configs/COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_1x.yaml \\
    MODEL.WEIGHTS /path/to/model.pkl
    ./configs/CenterNet2_Mv2-BiFPN_1280_4x.yaml MODEL.WEIGHTS ./output/CenterNet2/CenterNet2_Mv2-BiFPN_1280_4x/model_0139999.pth
     --tasks flop  --config-file ./configs/CenterNet2_v19_slim_FPN.yaml MODEL.WEIGHTS ./output/CenterNet2/CenterNet2_v19_slim_FPN/model_0111999.pth
   python analyze_model.py --num-inputs 100 --tasks flop  --config-file ./configs/CenterNet2_R2-101-DCN-BiFPN_1280_4x.yaml MODEL.WEIGHTS ./output/CenterNet2/OCenterNet2_R2-101-DCN-BiFPN_1280_4x/model_0139999.pth
"""
    )
    parser.add_argument(
        "--tasks",
        choices=["flop", "activation", "parameter", "structure"],
        required=True,
        nargs="+",
    )
    parser.add_argument(
        "--num-inputs",
        default=1,
        type=int,
        help="number of inputs used to compute statistics for flops/activations, "
        "both are data dependent.",
    )
    args = parser.parse_args()
    assert not args.eval_only
    assert args.num_gpus == 1

    cfg = setup(args)

    for task in args.tasks:
        {
            "flop": do_flop,
            "activation": do_activation,
            "parameter": do_parameter,
            "structure": do_structure,
        }[task](cfg)
