#!/usr/bin/env python3

"""
6.101 Lab:
Image Processing
"""

import math
import os
from PIL import Image

# NO ADDITIONAL IMPORTS ALLOWED!


def get_pixel(image, row, col, behavior):
    """
    Retrieves the pixel with the associated row and column.

    Args:
        image: the image dictionary
        row: the row number [0, #rows - 1]
        col: the column number [0, #cols - 1]
        behavior: wrap or extended or zero behavior if out of bounds

    Returns:
        The pixel with the associated row and column under
        wrap or extended behavior if necessary.
    """
    # BUG HERE: changed from col, row to row * numcols + col
    numcols = image["width"]
    match behavior:
        case "wrap":
            if row < 0 or row > image["height"] - 1:
                row = row % image["height"]
            if col < 0 or col > image["width"] - 1:
                col = col % image["width"]
            return image["pixels"][row * numcols + col]
        case "extend":
            if row < 0:
                row = 0
            elif row > image["height"] - 1:
                row = image["height"] - 1
            if col < 0:
                col = 0
            elif col > image["width"] - 1:
                col = image["width"] - 1
            return image["pixels"][row * numcols + col]
        case "zero":
            if (
                row < 0
                or row > image["height"] - 1
                or col < 0
                or col > image["width"] - 1
                ):
                return 0
            return image["pixels"][row * numcols + col]
        case "":
            return image["pixels"][row * numcols + col]

def set_pixel(image, row, col, color):
    """
    Sets the pixel with the associated row and column with the new color.

    Args:
        image: the image dictionary
        row: the row number [0, #rows - 1]
        col: the column number [0, #cols - 1]
        color: the color [0,255] to set the pixel to

    Returns:
        nothing
    """
    # BUG HERE: changed from row, col to row * j + col
    numcols = image["width"]
    image["pixels"][row * numcols + col] = color


def apply_per_pixel(image, func):
    """
    Applys each pixel in the image with a color according to the function without
    modifying the original image.

    Args:
        image: the image dictionary
        func: a lambda function that returns the color

    Returns:
        A new image with the new colors applied to each pixel
    """
    result = {
        "height": image["height"],
        "width": image["width"],  # BUG HERE: "widht" to width
        "pixels": image["pixels"].copy(),  # BUG HERE: change from empty
        # list to image pixels copy
    }
    # BUG HERE: changed from col, row to for row then for col
    for row in range(image["height"]):
        for col in range(image["width"]):
            color = get_pixel(image, row, col,"")  # BUG HERE:
            # changed from col, row to row, col
            new_color = func(color)
            set_pixel(result, row, col, new_color)  # BUG HERE: inside nested for loops
    return result


def inverted(image):
    """
    Inverts the pixel by subtracting its color by 255

    Args:
        image: the image dictionary

    Returns:
        A function that inverts each pixel
    """
    return apply_per_pixel(image, lambda color: 255 - color)
    # BUG HERE: subtract from 255 instead of 256


# HELPER FUNCTIONS


def correlate(image, kernel, boundary_behavior):
    """
    Compute the result of correlating the given image with the given kernel.
    `boundary_behavior` will one of the strings "zero", "extend", or "wrap",
    and this function will treat out-of-bounds pixels as having the value zero,
    the value of the nearest edge, or the value wrapped around the other edge
    of the image, respectively.

    if boundary_behavior is not one of "zero", "extend", or "wrap", return
    None.

    Otherwise, the output of this function should have the same form as a 6.101
    image (a dictionary with "height", "width", and "pixels" keys), but its
    pixel values do not necessarily need to be in the range [0,255], nor do
    they need to be integers (they should not be clipped or rounded at all).

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.

    DESCRIBE YOUR KERNEL REPRESENTATION HERE

    Kernel is a list of integers represented similarly to result["pixels"]
    with m x n dimensions
    """
    result = {
        "height": image["height"],
        "width": image["width"],
        "pixels": [0] * (image["height"] * image["width"]),
    }
    kernel_length = int(math.sqrt(len(kernel)))
    image_cols = image["width"]
    for row in range(image["height"]):
        for col in range(image["width"]):
            total = 0
            middle = int(kernel_length / 2)
            for rowk in range(kernel_length):
                for colk in range(kernel_length):
                    r = rowk - middle + row
                    c = colk - middle + col
                    pixel = get_pixel(image, r, c, boundary_behavior)
                    new_pixel = (
                                    kernel[rowk * kernel_length + colk]
                                    * pixel
                    )
                    total += new_pixel
                    result["pixels"][row * image_cols + col] = total
    return result

def round_and_clip_image(image):
    """
    Given a dictionary, ensure that the values in the "pixels" list are all
    integers in the range [0, 255].

    All values should be converted to integers using Python's `round` function.

    Any locations with values higher than 255 in the input should have value
    255 in the output; and any locations with values lower than 0 in the input
    should have value 0 in the output.
    """
    for i in range(len(image["pixels"])):
        val = image["pixels"][i]
        image["pixels"][i] = int(round(val))
        if val < 0:
            image["pixels"][i] = 0
        if val > 255:
            image["pixels"][i] = 255


# FILTERS


def blurred(image, kernel_size):
    """
    Return a new image representing the result of applying a box blur (with the
    given kernel size) to the given input image.

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.
    """
    # first, create a representation for the appropriate n-by-n kernel (you may
    # wish to define another helper function for this)
    bkernel = blurkernel(kernel_size)
    # print("bkernel ", bkernel)
    # then compute the correlation of the input image with that kernel
    result = correlate(image, bkernel, "extend")
    # and, finally, make sure that the output is a valid image (using the
    # helper function from above) before returning it.

    #UNCOMMENT OUT THIS LINE IF YOU ARE NOT USING SHARPEN
    round_and_clip_image(result)
    return result

def blurkernel(kernel_size):
    """
    Generates a n x n kernel with identical elements
    and with sum 1

    Args:
        kernel_size: kernel_size used to build the
        n x n blur

    Returns:
        The kernel with the specified dimensions
    """
    kernel = []
    for _ in range(kernel_size ** 2):
        kernel.append(1 / (kernel_size * kernel_size))
    return kernel

def sharpened(image, kernel_size):
    """
    Sharpens the image using a blur kernel and the
    formula O(r, c) = 2I(r, c) - B(r, c)

    Args:
        image: the image dictionary
        kernel_size: kernel_size used to build the
        blurred version of the image

    Returns:
        The image sharpened, clipped and rounded according
        to the formula above.
    """
    blurredimage = blurred(image, kernel_size)
    sharp_image = {"height":image["height"],
        "width":image["width"],
        "pixels":image["pixels"].copy()
    }
    for row in range(image["height"]):
        for col in range(image["width"]):
            sharp_image["pixels"][row * image["width"] + col] = (2 *
            image["pixels"][row * image["width"] + col]
            - blurredimage["pixels"][row * image["width"] + col])
    round_and_clip_image(sharp_image)
    return sharp_image

def edges(image):
    """
    Implement a sobel operator on an image, which detects edges
    in images

    Args:
        image: the image dictionary

    Returns:
        The image with the Sobel operator applied to it.
    """
    kernel1 = [
        -1, -2, -1,
        0,  0,  0,
        1,  2,  1,
    ]
    kernel2 = [
        -1, 0, 1,
        -2,  0,  2,
        -1,  0,  1,
    ]
    output1 = correlate(image, kernel1, "extend")
    output2 = correlate(image, kernel2, "extend")

    final_output = {
        "height":image["height"],
        "width":image["width"],
        "pixels":image["pixels"].copy()
    }
    for i in range(len(image["pixels"])):
        final_output["pixels"][i] = round(math.sqrt(
            output1["pixels"][i] ** 2 + output2["pixels"][i] ** 2
        ))
    round_and_clip_image(final_output)
    return final_output

# HELPER FUNCTIONS FOR DISPLAYING, LOADING, AND SAVING IMAGES


def print_greyscale_values(image):
    """
    Given a greyscale image dictionary, prints a string representation of the
    image pixel values to the terminal. This function may be helpful for
    manually testing and debugging tiny image examples.

    Note that pixel values that are floats will be rounded to the nearest int.
    """
    out = f"Greyscale image with {image['height']} rows"
    out += f" and {image['width']} columns:\n "
    space_sizes = {}
    space_vals = []

    col = 0
    for pixel in image["pixels"]:
        val = str(round(pixel))
        space_vals.append((col, val))
        space_sizes[col] = max(len(val), space_sizes.get(col, 2))
        if col == image["width"] - 1:
            col = 0
        else:
            col += 1

    for col, val in space_vals:
        out += f"{val.center(space_sizes[col])} "
        if col == image["width"] - 1:
            out += "\n "
    print(out)


def load_greyscale_image(filename):
    """
    Loads an image from the given file and returns a dictionary
    representing that image.  This also performs conversion to greyscale.

    Invoked as, for example:
       i = load_greyscale_image("test_images/cat.png")
    """
    with open(filename, "rb") as img_handle:
        img = Image.open(img_handle)
        img_data = img.getdata()
        if img.mode.startswith("RGB"):
            pixels = [
                round(0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2]) for p in img_data
            ]
        elif img.mode == "LA":
            pixels = [p[0] for p in img_data]
        elif img.mode == "L":
            pixels = list(img_data)
        else:
            raise ValueError(f"Unsupported image mode: {img.mode}")
        width, height = img.size
        return {"height": height, "width": width, "pixels": pixels}


def save_greyscale_image(image, filename, mode="PNG"):
    """
    Saves the given image to disk or to a file-like object.  If filename is
    given as a string, the file type will be inferred from the given name.  If
    filename is given as a file-like object, the file type will be determined
    by the "mode" parameter.
    """
    # make folders if they do not exist
    path, _ = os.path.split(filename)
    if path and not os.path.exists(path):
        os.makedirs(path)

    # save image in folder specified (by default the current folder)
    out = Image.new(mode="L", size=(image["width"], image["height"]))
    out.putdata(image["pixels"])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


if __name__ == "__main__":
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place for
    # generating images, etc.
    # im = load_greyscale_image('bluegill.png')
    # result = inverted(im)
    # save_greyscale_image(result, "invbluegill.png")

    #image = load_greyscale_image("test_images/pigbird.png")
    #center = load_greyscale_image("test_images/centered_pixel.png")
    # kernel = [0,0,0,0,0,0,0,0,0,0,0,0,0,
    #           0,0,0,0,0,0,0,0,0,0,0,0,0,
    #           1,0,0,0,0,0,0,0,0,0,0,0,0,
    #           0,0,0,0,0,0,0,0,0,0,0,0,0,
    #           0,0,0,0,0,0,0,0,0,0,0,0,0,
    #           0,0,0,0,0,0,0,0,0,0,0,0,0,
    #           0,0,0,0,0,0,0,0,0,0,0,0,0,
    #           0,0,0,0,0,0,0,0,0,0,0,0,0,
    #           0,0,0,0,0,0,0,0,0,0,0,0,0,
    #           0,0,0,0,0,0,0,0,0,0,0,0,0,
    #           0,0,0,0,0,0,0,0,0,0,0,0,0,
    #           0,0,0,0,0,0,0,0,0,0,0,0,0,
    #           0,0,0,0,0,0,0,0,0,0,0,0,0]
    # image = {"height": 3,
    #          "width": 2,
    #          "pixels":
    #         [20, 40,
    #          60, 80,
    #          100, 120]}
    # kernel = [0, 0, 0,
    #           0, 0, 1,
    #           0, 0, 0]
    #print(correlate(image, kernel, "wrap"))
    # print(center)
    # print(correlate(center, kernel, "wrap"))
    # zeroresult = correlate(image, kernel, "zero")
    # save_greyscale_image(zeroresult, "zeropigbird.png")
    # exresult = correlate(image, kernel, "extend")
    # save_greyscale_image(exresult, "expigbird.png")
    # wrapresult = correlate(image, kernel, "wrap")
    # save_greyscale_image(wrapresult, "wrappigbird.png")

    # cat = load_greyscale_image("test_images/cat.png")
    # print_greyscale_values(cat)
    # blurcat = blurred(cat, 13)
    # print_greyscale_values(blurcat)
    # save_greyscale_image(blurcat, "blurcat.png")

    # python = load_greyscale_image("test_images/python.png")
    # sharppython = sharpened(python, 11)
    # save_greyscale_image(sharppython, "sharppython.png")

    construct = load_greyscale_image("test_images/construct.png")
    edgeconstruct = edges(construct)
    save_greyscale_image(edgeconstruct, "edgeconstruct.png")
