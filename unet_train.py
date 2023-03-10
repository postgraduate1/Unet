from PIL import Image
import numpy as np

def rand(a=0, b=1):
    return np.random.rand()*(b-a) + a
def get_random_resize(image, label, input_shape, jitter=.3, hue=.1, sat=1.5, val=1.5):
    # 输入image为jpg原图，label是png标签图片都是用Image.open()打开，打开后仅保留一维色彩，一个像素点只有一个数值
    
    
    # 使用labelme制作的png的标签图片u能用cv2打开，mpimg打开后是一维数值，cv2打开是被分解了的
    # 比如labelme制作的png其中一个像素为3，在cv2打开就是[0,128,128]
    # 用arcgis制作的tif文件cv2打开rgb都一样，也和mpimg一样
    label = Image.fromarray(np.array(label))
    h, w = input_shape
    # resize image
    rand_jit1 = rand(1-jitter,1+jitter)
    rand_jit2 = rand(1-jitter,1+jitter)
    new_ar = w/h * rand_jit1/rand_jit2

    scale = rand(0.25, 2)
    if new_ar < 1:
        nh = int(scale*h)
        nw = int(nh*new_ar)
    else:
        nw = int(scale*w)
        nh = int(nw/new_ar)
    image = image.resize((nw,nh), Image.BICUBIC)
    label = label.resize((nw,nh), Image.NEAREST)
    label = label.convert("L")
    
    # flip image or not
    flip = rand()<.5
    if flip: 
        image = image.transpose(Image.FLIP_LEFT_RIGHT)
        label = label.transpose(Image.FLIP_LEFT_RIGHT)
    
    # place image
    dx = int(rand(0, w-nw))
    dy = int(rand(0, h-nh))
    new_image = Image.new('RGB', (w,h), (128,128,128))
    new_label = Image.new('L', (w,h), (0))
    new_image.paste(image, (dx, dy))
    new_label.paste(label, (dx, dy))
    image = new_image
    label = new_label

    # distort image
    hue = rand(-hue, hue)
    sat = rand(1, sat) if rand()<.5 else 1/rand(1, sat)
    val = rand(1, val) if rand()<.5 else 1/rand(1, val)
    x = cv2.cvtColor(np.array(image,np.float32)/255, cv2.COLOR_RGB2HSV)
    x[..., 0] += hue*360
    x[..., 0][x[..., 0]>1] -= 1
    x[..., 0][x[..., 0]<0] += 1
    x[..., 1] *= sat
    x[..., 2] *= val
    x[x[:,:, 0]>360, 0] = 360
    x[:, :, 1:][x[:, :, 1:]>1] = 1
    x[x<0] = 0
    image_data = cv2.cvtColor(x, cv2.COLOR_HSV2RGB)
    return image_data,label

def letterbox_image(image, label, size):
    # 输入为Image.open(image_path)，Image.open(Label_path)
    label = Image.fromarray(np.array(label))

    '''resize image with unchanged aspect ratio using padding'''
    iw, ih = image.size
    w, h = size
    scale = min(w/iw, h/ih)
    nw = int(iw*scale)
    nh = int(ih*scale)

    image = image.resize((nw, nh), Image.BICUBIC)
    new_image = Image.new('RGB', size, (128, 128, 128))
    new_image.paste(image, ((w-nw)//2, (h-nh)//2))

    label = label.resize((nw, nh), Image.NEAREST)
    new_label = Image.new('L', size, (0))
    new_label.paste(label, ((w-nw)//2, (h-nh)//2))
    return new_image, new_label

