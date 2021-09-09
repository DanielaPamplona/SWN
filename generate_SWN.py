from os import makedirs
from os.path import exists,join
import argparse
import numpy as np
from skimage.io import imsave



######### Parsing parameters ########################
parser = argparse.ArgumentParser(description = 'Parser to generate SWN')
parser.add_argument('-T', type = int, help = 'Number of images',required = True)
parser.add_argument('-N', type = int, help = 'Image size in pixels',required = True)
parser.add_argument('-beta', type = int, help = 'Block size in pixels',required = True)
parser.add_argument('-alpha', type = int, help = 'Baseline shift size in pixels',required = True)
parser.add_argument('-o', type = str, help = "Output folder path. It is recommended to use the absolute path.", dest = 'output_folder_path',required = True)

args = vars(parser.parse_args())#parsing the arguments, now they are all in the dictionary args



######### Verifying parameters and create dependent ones ########################

if args['alpha'] == 0:
    print('Warning: alpha is zero, this is not shifted white noise, but basic white noise. Continuing... ')
    args['S'] = 0
elif args['beta']%args['alpha']!=0:
    print("The block size must be proportional to the baseline shift. Aborting...")
    exit
else:
    args['S'] = int(args['beta']/args['alpha']) #number of possible shifts in each direction

if args['N']%args['beta']!=0:
    print("The number of pixels is not proportional to the block size. Even if considering no shift, there will be a partial block on the right and bottom of each image")

args['B'] = int(np.ceil(args['N']/args['beta'])) #number of blocks in each direction, the total number of blocks is B^2



######### Preparing for saving the files ########################

if not(exists(args['output_folder_path'])): #creates, if necessary, the output folder 
    makedirs(args['output_folder_path'])

args['number_of_digits'] = int(np.ceil(np.log10(args['T']))) #number of digits used to generate the file name for each image
                                        


######### Functions to generate the SWN ########################

def generate_image(args):
    img = np.zeros((args['N']+args['beta'],args['N']+args['beta'])) #first we generate a larger image with B+1 blocks in each direction. Later we crop this image. 
    for b_horizontal in range(args['B']+1):
        for b_vertical in range(args['B']+1):
            img[b_horizontal*args['beta']:(b_horizontal+1)*args['beta'], b_vertical*args['beta']:(b_vertical+1)*args['beta']] = np.random.randint(2) #select randomly the color of each block (black = 0, white = 1)
    [step_horizontal,step_vertical] = np.random.randint(args['S'],size = 2)#select randomly the number of steps to multiply by the baseline in each direction
    shift_horizontal = step_horizontal*args['alpha']
    shift_vertical = step_vertical*args['alpha']
    return img[shift_horizontal:shift_horizontal+args['N'],shift_vertical:shift_vertical+args['N']] #cropping the image to return the shifted image

def generate_dataset(args):
    for image_number in range(args['T']):
        image_file_path = join(args['output_folder_path'],'image_'+np.str(image_number).zfill(args['number_of_digits'])+'.png') #creating the file path
        image = generate_image(args)
        image *=255 #to save images as png one should use integers between 0 (black) and 255 (white)
        imsave(image_file_path,image.astype('uint8'),check_contrast=False)
                                                                                         


######### Executable ########################
    
def main(args):
    generate_dataset(args)

if __name__ =="__main__":
    main(args)
