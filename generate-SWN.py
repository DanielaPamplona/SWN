from os import makedirs
from os.path import exists,join,abspath
import argparse
import numpy as np
from skimage.io import imsave
from json import dump
from matplotlib import pyplot as plt


######### Parsing parameters ########################
parser = argparse.ArgumentParser(description = 'Parser to generate SWN')
parser.add_argument('-T', type = int, help = 'Number of images',required = True)
parser.add_argument('-N', type = int, help = 'Image size in pixels',required = True)
parser.add_argument('-beta', type = int, help = 'Block size in pixels',required = True)
parser.add_argument('-alpha', type = int, help = 'Baseline shift size in pixels',required = True)
parser.add_argument('-o', type = str, help = "Output folder path", dest = 'output-folder-path',required = True)

args = vars(parser.parse_args())#parsing the arguments, now they are all in the dictionary args




                                        
######### IO functions ########################################

def verify_and_create_and_save_args(args): 
    args = set_S(args)
    args = set_B(args)
    args = set_number_of_digits_to_save_image(args)
    args = set_output_folder_path(args)
    verify_border(args)
    make_output_folder(args)
    save_args(args)
    return args

def set_S(args):
    if args['alpha'] == 0:
        print('Warning: alpha is zero, this is not shifted white noise, but basic white noise. Continuing... ')
        args['S'] = 0
    elif args['beta']%args['alpha']!=0:
        print("The block size must be proportional to the baseline shift. Aborting...")
        return exit()
    else:
        args['S'] = int(args['beta']/args['alpha']) #number of possible shifts in each direction
    return args
    
def set_B(args):
    args['B'] = int(np.ceil(args['N']/args['beta'])) #number of blocks in each direction, the total number of blocks is B^2
    return args

def set_number_of_digits_to_save_image(args):
    args['number-of-digits'] = int(np.ceil(np.log10(args['T']))) #number of digits used to generate the file name for each image
    return args


def set_output_folder_path(args):
    args['output-folder-path'] = abspath(args['output-folder-path'])
    return args


def verify_border(args):
    if args['N']%args['beta']!=0:
        print("The number of pixels is not proportional to the block size. Even if considering no shift, there will be a partial block on the right and bottom of each image")    
    
def make_output_folder(args):
    if not(exists(args['output-folder-path'])): #creates, if necessary, the output folder 
        makedirs(args['output-folder-path'])

def save_args(args): #saves the arguments in a txt file in the output folder
    with open(join(args['output-folder-path'],'args.txt'), 'w') as f: #saving all the parameters in a file.
        dump(args,f,indent = 2) 


def generate_histogram(shift_vertical_list,shift_horizontal_list,args):
    image_file_path = join(args['output-folder-path'],'shifts-distribution.png') #creating the file path
    bins_edges = np.arange(args['S']+1)*args['alpha']
    bins_labels = bins_edges[:-1]
    plt.figure(figsize = [5,8])
    plt.suptitle('Shifts\' distribution')
    plt.subplot(2,1,1)
    plt.hist(shift_vertical_list,bins=bins_edges,align = 'left',density = True)
    plt.xticks(bins_labels)
    plt.ylabel('Probability')
    plt.title('Vertical')
    plt.xlabel('Step size (in px)')
    plt.subplot(2,1,2)
    plt.hist(shift_horizontal_list,bins=bins_edges,align = 'left',density = True)
    plt.xticks(bins_labels)
    plt.ylabel('Probability')
    plt.xlabel('Step size (in px)')
    plt.title('Horizontal')
    plt.tight_layout(w_pad = 1.5)
    plt.savefig(image_file_path)

######### Functions to generate the SWN ########################

def generate_image(args):
    img = np.zeros((args['N']+args['beta'],args['N']+args['beta'])) #first we generate a larger image with B+1 blocks in each direction. Later we crop this image. 
    for b_horizontal in range(args['B']+1):
        for b_vertical in range(args['B']+1):
            img[b_horizontal*args['beta']:(b_horizontal+1)*args['beta'], b_vertical*args['beta']:(b_vertical+1)*args['beta']] = np.random.randint(2) #select randomly the color of each block (black = 0, white = 1)
    [step_horizontal,step_vertical] = np.random.randint(args['S'],size = 2)#select randomly the number of steps to multiply by the baseline in each direction
    shift_horizontal = step_horizontal*args['alpha']
    shift_vertical = step_vertical*args['alpha']
    shifted_img = img[shift_vertical:shift_vertical+args['N'],shift_horizontal:shift_horizontal+args['N']] #cropping the image to return the shifted image
    return [shifted_img,shift_vertical,shift_horizontal] 

def generate_dataset(args):
    verify_and_create_and_save_args(args)
    shift_vertical_list = []
    shift_horizontal_list = []
    for image_number in range(args['T']):
        image_file_path = join(args['output-folder-path'],'image-'+str(image_number).zfill(args['number-of-digits'])+'.png') #creating the file path
        [shifted_img,shift_vertical,shift_horizontal] = generate_image(args)
        shifted_img *=255 #to save images as png one should use integers between 0 (black) and 255 (white)
        imsave(image_file_path,shifted_img.astype('uint8'),check_contrast=False)
        shift_vertical_list.append(shift_vertical)
        shift_horizontal_list.append(shift_horizontal)
    generate_histogram(shift_vertical_list,shift_horizontal_list,args) #save the shifts' distributions in a png file on the output folder
    
    
######### Executable ########################
    
def main(args):
    generate_dataset(args)

if __name__ =="__main__":
    main(args)
