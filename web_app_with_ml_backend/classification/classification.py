import os

import torch
import torchvision
import torch.nn.functional as F
import torch.nn as nn
from torchvision import transforms
from torch.utils.data import Dataset, DataLoader, Subset
from torch.optim.lr_scheduler import ReduceLROnPlateau, OneCycleLR
import pandas as pd
import numpy as np
import gc
import os
import time
import datetime
import warnings
from efficientnet_pytorch import EfficientNet
import cv2
from PIL import Image, ImageFilter    

class testDataset(Dataset):
    def __init__(self, transforms = None,path=None):
        """
        Class initialization
        Args:
            df (pd.DataFrame): DataFrame with data description
            data (np.ndarray): resized images data in a shape of (HxWxC)
            train (bool): flag of whether a training dataset is being initialized or testing one
            transforms: image transformation method to be applied
        """
        self.transforms = transforms
        
        self.path=path
        
    def __getitem__(self, index):
        path = self.path
        
        image = cv2.imread(path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = transforms.ToPILImage()(image)

        if self.transforms:
            image = self.transforms(image)
            #image=image['image']
        return image
    
    def __len__(self):
        return 1


def predict(img_path, weight_path):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    test_transform = transforms.Compose([
            transforms.Resize((256,256)),
            transforms.ToTensor(),
            transforms.Normalize((0.485, 0.456, 0.406),(0.229, 0.224, 0.225)),
            
        ])

    test = testDataset(transforms=test_transform, path=img_path)  
    test_loader = DataLoader(dataset=test, batch_size=1, shuffle=True)

    model = EfficientNet.from_pretrained('efficientnet-b0')
    in_features = model._fc.in_features
    classifier =nn.Linear(in_features, 1)
    model._fc=classifier

    model.load_state_dict(torch.load('classification/saved_weight/current_checkpoint.pt', map_location='cpu'),strict=True)
    model.cpu()
    model.eval()  # switch model to the evaluation mode
    
    with torch.no_grad():
        # Predicting on validation set once again to obtain data for OOF
        preds = torch.zeros((1, 1), dtype=torch.float32, device=device)

        # Predicting on test set
        for i, x_test in enumerate(test_loader):
            #x_test = torch.tensor(x_test, device='cpu', dtype=torch.float32)
            x_test = x_test.clone().detach().requires_grad_(True)
            z_test = model(x_test)
            z_test = torch.sigmoid(z_test)
            preds[i*x_test.shape[0]:i*x_test.shape[0] + x_test.shape[0]] += z_test
    print(preds[0][0].item())
    return preds[0][0]

# predict('input_imgs/mildDem10.jpg', 'classification/saved_weight/current_checkpoint.pt')




