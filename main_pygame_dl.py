import os
import pygame
import torch
import numpy as np

from lib.displayer import displayer
from lib.utils import mat_distance, load_image
from lib.CAModel import CAModel
from lib.utils_vis import to_rgb, make_seed

os.environ['KMP_DUPLICATE_LIB_OK']='True'

eraser_radius = 3
pix_size = 8
_map_shape = (72,72)
CHANNEL_N = 16
CELL_FIRE_RATE = 0.5
model_path = "models/grav.pth"
paths = ["models/grav.pth", "models/cradle.pth"]
path_i = 0
device = torch.device("cpu")
h, w = _map_shape
_rows = np.arange(_map_shape[0]).repeat(_map_shape[1]).reshape([_map_shape[0],_map_shape[1]])
_cols = np.arange(_map_shape[1]).reshape([1,-1]).repeat(_map_shape[0],axis=0)
_map_pos = np.array([_rows,_cols]).transpose([1,2,0])

# _map = make_seed(_map_shape, CHANNEL_N)
_map = np.zeros([h,w, CHANNEL_N], np.float32)
seed_img = load_image("../data/grav0.png", resize_shape=(h, w))
_map[:, :, :4] = seed_img

model = CAModel(CHANNEL_N, CELL_FIRE_RATE, device).to(device)
model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
output = model(torch.from_numpy(_map.reshape([1,_map_shape[0],_map_shape[1],CHANNEL_N]).astype(np.float32)), 1)

disp = displayer(_map_shape, pix_size)

isMouseDown = False
running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                _map = np.zeros([h,w, CHANNEL_N], np.float32)
                seed_img = load_image("../data/grav0.png", resize_shape=(h, w))
                _map[:, :, :4] = seed_img
                output = model(torch.from_numpy(_map.reshape([1,_map_shape[0],_map_shape[1],CHANNEL_N]).astype(np.float32)), 1)
                

            elif event.key == pygame.K_n:
                path_i = (path_i + 1) % len(paths)
                print("Loading model: ", paths[path_i])
                model_path = paths[path_i]
                model = CAModel(CHANNEL_N, CELL_FIRE_RATE, device).to(device)
                model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
                

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                isMouseDown = True

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                isMouseDown = False

    if isMouseDown:
        try:
            mouse_pos = np.array([int(event.pos[1]/pix_size), int(event.pos[0]/pix_size)])
            should_keep = (mat_distance(_map_pos, mouse_pos)>eraser_radius).reshape([_map_shape[0],_map_shape[1],1])
            output = torch.from_numpy(output.detach().numpy()*should_keep)
        except AttributeError:
            pass

    output = model(output, 1)

    _map = to_rgb(output.detach().numpy()[0])
    disp.update(_map)
