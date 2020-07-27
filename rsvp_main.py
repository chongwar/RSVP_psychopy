import os
import warnings
import numpy as np
from win32api import GetSystemMetrics
from psychopy import visual, core, parallel
from biosemi import ActiveTwo

warnings.filterwarnings('ignore')


def generate_texture(win, img_dir):
    img_num = len(os.listdir(img_dir))
    texture = []
    for _img in os.listdir(img_dir):
        img = os.path.join(img_dir, _img)
        texture_tmp = visual.ImageStim(win, image=img)
        texture.append(texture_tmp)
    return img_num, texture


def draw_fixation(win, interval=2):
    length, width = 120, 3.5
    _w, _h = length / w, length / h
    l, r, u, d = (-_w, 0), (_w, 0), (0, -_h), (0, _h)
    line_lr = visual.Line(win, l, r, lineWidth=width)
    line_ud = visual.Line(win, u, d, lineWidth=width)
    line_lr.draw()
    line_ud.draw()
    win.flip()
    core.wait(interval)


# initial parallel port
p_port = parallel.ParallelPort(address=0xAFF8)

w = GetSystemMetrics(0)
h = GetSystemMetrics(1)
win = visual.Window(size=(w, h), fullscr=False, color=(-1, -1, -1))

# generate target and notarget textures
tar_dir = 'images/tar'
notar_dir = 'images/notar'
tar_num, texture_tar = generate_texture(win, tar_dir)
notar_num, texture_notar = generate_texture(win, notar_dir)

# parameters
host = '10.170.33.219'
sfreq = 1024
port = 1111
channle_num = 65
trial_num = 2
seq_num = 50
display_time = 0.05
duration = seq_num * display_time + 0.5
tar_posi = [5, 15, 25, 35]
data = []

for trial in range(trial_num):
    draw_fixation(win)
    tar_rand_idx = np.random.permutation(tar_num)
    notar_rand_idx = np.random.permutation(notar_num)
    tar_count = 0
    notar_count = 0
    active_two = ActiveTwo(host=host, sfreq=sfreq, 
                           port=port, nchannels=channle_num)
    for seq in range(seq_num):
        if seq in tar_posi:
            trigger = 4
            texture_tar[tar_rand_idx[tar_count]].draw()
            tar_count += 1
        else:
            trigger = 16 if seq == 0 else 1
            texture_notar[notar_rand_idx[notar_count]].draw()
            notar_count += 1
        
        # send trigger by parallel port
        p_port.setData(trigger)  
        win.flip()
        core.wait(display_time)
    
    win.flip()
    # read raw eeg data from BioSemi ActiveTwo device
    raw_data = active_two.read(duration=duration)
    data.append(raw_data)
    core.wait(1)

win.close()

np.save('data', np.array(data))
print('Finish.')
