import os
import sys
import numpy as np
import cv2



# define pipeline function for our computer vision processing
def cvpipeline(*functions):
    def result_cvpipeline(input_image):
        output_image = input_image
        for func in list(functions):
            output_image = func(output_image)
        return output_image

    return result_cvpipeline


# reading all images in input folder
def imread_generator(folder):
    files = os.listdir(folder)
    return (cv2.imread(os.path.join(folder, filename)) for filename in files)



def sum_to_image(x):
    return np.floor(x / (max(x.ravel())) * 255).astype('uint8')


def mythreshold(image,value):
    retval, threshold = cv2.threshold(image, value, 255, cv2.THRESH_BINARY)
    return threshold




def findBlur(tempfolder, intentionalBlur=True):
    # processing pipes

    kernel = np.ones((5, 5), np.uint8)

    nabla_I_pipe = cvpipeline(lambda x: cv2.GaussianBlur(x, (5, 5), 0), lambda x: cv2.Laplacian(x, ddepth=-1, ksize=1))
    I_pipe = cvpipeline(lambda x: cv2.adaptiveThreshold(x, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 101, 5))
    continuous_change_pipe = cvpipeline(lambda x: cv2.GaussianBlur(x, (5, 5), 0),
                                        lambda x: (x - x.min()) * 255 / (x.max() - x.min()))

    # post pipes
    nabla_I_histogram_pipe = cvpipeline(lambda x: sum_to_image(x), lambda x: mythreshold(x, 40),
                                        lambda x: cv2.dilate(x, np.ones((3, 3), np.uint8),
                                                             iterations=1))  # used to be 50
    nabla_I_post_pipe = cvpipeline(lambda x: sum_to_image(x),
                                   lambda x: cv2.adaptiveThreshold(x, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                                                   cv2.THRESH_BINARY, 501, 1),
                                   lambda x: cv2.dilate(x, kernel, iterations=1), lambda x: cv2.blur(x, (81, 81), 0),
                                   lambda x: cv2.adaptiveThreshold(x, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                                                   cv2.THRESH_BINARY, 101, 5), )
    I_post_pipe = cvpipeline(lambda x: sum_to_image(x),
                             lambda x: mythreshold(x, np.mean(x.ravel()) - 2 * np.std(x.ravel())))  # used to be 100
    continous_post_pipe = cvpipeline(lambda x: sum_to_image(x),
                                     lambda x: cv2.adaptiveThreshold(x, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                                                     cv2.THRESH_BINARY, 701,
                                                                     1 + 0.5 * np.std(x.ravel())),
                                     lambda x: cv2.dilate(x, np.ones((3, 3)), iterations=3))

    third_process = cvpipeline(lambda x: cv2.cvtColor(x, cv2.COLOR_BGR2GRAY),
                               lambda x: cv2.GaussianBlur(x, (5, 5), 0),
                               lambda x: (x - x.min()) * 255 / (x.max() - x.min())
                               )

    image_shape = [2032, 2032]
    nabla_I_sum = np.zeros(image_shape)
    I_sum = np.zeros(image_shape)
    continuous_sum = np.zeros(image_shape)
    count = 0

    images = imread_generator(tempfolder)
    files = os.listdir(tempfolder)
    im = cv2.imread(os.path.join(tempfolder, files[0]))
    temp = third_process(im)
    for (idx, image) in enumerate(images):
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        nabla_I_sum += nabla_I_pipe(gray_image)
        I_sum += I_pipe(gray_image)
        delta_temp = continuous_change_pipe(gray_image)
        continuous_sum += abs(delta_temp - temp)
        temp = delta_temp
        count = count + 1
    method_1 = nabla_I_histogram_pipe(nabla_I_sum)
    method_2 = nabla_I_post_pipe(nabla_I_sum)
    method_3 = I_post_pipe(I_sum)
    method_4 = continous_post_pipe(continuous_sum)
    cond = (method_1 == 0) | ((method_2 == 0) & (method_4 == 0)) | ((method_3 == 0) & (method_4 == 0))
    final_result = np.where(cond, 255, 0).astype(np.uint8)
    final_result = cv2.dilate(final_result, np.ones((5, 5), np.uint8), iterations=3)

    return final_result


if __name__ == "__main__":


    args = sys.argv[1:]

    if not args[0]:
        print("Directory is invalid")
        sys.exit()

    path_to_images=args[0]

    subfolder = ['cam_0', 'cam_1', 'cam_2', 'cam_3', 'cam_5']
    input_folders = [os.path.join(path_to_images, sub) for sub in subfolder]
    output_folder = os.path.join(path_to_images, 'results/')

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    for i in input_folders:


         output=findBlur(i)
         cv2.imwrite(output_folder+i[-1]+'_output.jpg',output)
