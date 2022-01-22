import torch
import numpy as np
import pickle
num_class =1
pretrained_weights  = torch.load('models/CenterNet2_R50_1x.pth')
pretrained_weights['iteration']=0
pretrained_weights['model']["roi_heads.box_predictor.0.cls_score.weight"].resize_(num_class+1,1024)
pretrained_weights['model']["roi_heads.box_predictor.0.cls_score.bias"].resize_(num_class+1)
pretrained_weights['model']["roi_heads.box_predictor.1.cls_score.weight"].resize_(num_class+1,1024)
pretrained_weights['model']["roi_heads.box_predictor.1.cls_score.bias"].resize_(num_class+1)
pretrained_weights['model']["roi_heads.box_predictor.2.cls_score.weight"].resize_(num_class+1,1024)
pretrained_weights['model']["roi_heads.box_predictor.2.cls_score.bias"].resize_(num_class+1)
torch.save(pretrained_weights, "models/CenterNet2_%d.pth"%num_class)

