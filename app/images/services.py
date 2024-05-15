from fastapi import UploadFile, \
             File, HTTPException
import requests
import cv2
import numpy as np
import base64
import imghdr

MAX_SIZE = 5000000  # 5 MB ish(for pepe's sake), should ideally be fettched from some config service, or maintained using database CRUD operations or s3, or a simple yaml file.
IMAGE_SAMPLE_SIZE = 100


# alternate functions to the deprecated imghdr library.
def is_jpeg(data):
    return data.startswith(b'\xFF\xD8\xFF')


def is_png(data):
    return data.startswith(b'\x89PNG\r\n\x1a\n')

def guess_content_type(data):
    if is_jpeg(data):
        return 'jpeg'
    elif is_png(data):
        return 'png'
    else:
        return 'invalid'

async def validate_image(file: UploadFile = File(...)):
    """ performs validation of both form data headers, and the binary data, as well as limits content length to less than 5 MB """ 
    if file is None:
        raise HTTPException(status_code=400, detail="Either file or URL must be provided.")
    
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Content-type error. Only JPEG and PNG files allowed.")  # https://www.youtube.com/watch?v=h06ZkqM_7qM
    
    content = await file.read()
    
    # Find Mime type from bytes, to reject all other MIME types, or bad JPEG and PNG encodings
    #image_type = imghdr.what(None, h=content)
    
    # use primitive method of guessing content type
    image_type = guess_content_type(content)

    if image_type not in ['jpeg', 'png']:
        raise HTTPException(status_code=400, detail="Content is either not a JPEG or PNG image or is encoded wrong.")

    file_size = len(content)
    if file_size > MAX_SIZE:
        raise HTTPException(status_code=400, detail=f"Image size exceeds the maximum allowed size of {MAX_SIZE} bytes.")
    
    return {"image_data": content, "content_type": image_type}

    """ #optional logic for URLs
    elif url:
        response = requests.get(url)
        
        if response.status_code >= 200 and response.status_code < 300:
            raise HTTPException(status_code=400, detail="Invalid URL. Response code: {response.status_code}")
        
        content_type = response.headers.get('Content-Type', '')
        if content_type not in ["image/jpeg", "image/png"]:
            raise HTTPException(status_code=400, detail="Only JPEG and PNG files allowed. Try another file.")
        
        content_length = int(response.headers.get('Content-Length', MAX_SIZE+1)) # avoid invalid requests

        if content_length > MAX_SIZE:
            raise HTTPException(status_code=400, detail=f"Content length the maximum allowed size of {MAX_SIZE} bytes.")

        content_type = file.content_type.split('/')[1]  # needs to be made into a method
        return {"image": response.content, "content_type": content_type}
    """


async def validate_multiform_data(file1: UploadFile = File(...), file2: UploadFile = File(...)):
    """ Handles multiple files. """
    return [await validate_image(file=file1), await validate_image(file=file2)]


class ImageHandler():
    def __init__(self, image_data: bytes, width: int, 
                 height: int, content_type: str) -> None:
        self.image_data = image_data
        self.width = width
        self.height = height
        self.image_type = content_type

    def _convert_to_array(self):
        # Convert bytes to 3d numpy array representing pixel intensities.
        file_bytes = np.asarray(bytearray(self.image_data), dtype=np.uint8)
        return cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        
    def crop_center(self):
        # Convert file object to numpy array

        image = self._convert_to_array()
        img_height, img_width = image.shape[:2]
        
        crop_width = self.width
        crop_height = self.height

        # Calculate padding if necessary
        pad_width = max(crop_width - img_width, 0)
        pad_height = max(crop_height - img_height, 0)
        
        # Calculate cropping dimensions
        start_x = max(img_width // 2 - (crop_width // 2), 0)
        end_x = min(start_x + crop_width, img_width)
        start_y = max(img_height // 2 - (crop_height // 2), 0)
        end_y = min(start_y + crop_height, img_height)
        
        # Pad image if necessary
        padded_img = cv2.copyMakeBorder(image, pad_height // 2, pad_height // 2, pad_width // 2, pad_width // 2, cv2.BORDER_CONSTANT)
        
        # Crop the padded image
        cropped_img = padded_img[start_y:end_y, start_x:end_x]
        
        # Convert cropped image to base64 encoded data
        success, encoded_image = cv2.imencode('.'+self.image_type, cropped_img)
        if success:
            base64_encoded_image = base64.b64encode(encoded_image)
            return base64_encoded_image
        else: 
            HTTPException(status_code=422, detail="The server is unable to process this content for now.")
    
    def bytes_to_channels(self):
        # Convert byte data to numpy array
        image = self._convert_to_array()

        # Split image into color channels
        b, g, r = cv2.split(image)
        return r.flatten(), g.flatten(), b.flatten()
    
    def compute_average_hash(self, hash_size=8):
        # Convert bytes to numpy array
        image = self._convert_to_array()

        # using an aHash (average hash) algorithm.
        resized = cv2.resize(image, (hash_size, hash_size))
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        average_pixel = gray.mean()

        # Generate binary hash
        hash_value = ""
        for i in range(hash_size):
            for j in range(hash_size):
                if gray[i, j] >= average_pixel:
                    hash_value += "1"
                else:
                    hash_value += "0"

        # Convert to hex string
        hex_value = hex(int(hash_value, 2))[2:]
        return hex_value


def compute_avg_cosine_similarity(image1: ImageHandler, image2: ImageHandler):
    """ 
        computes the cosine similarity of each channel and then averages it.
        This needs to optimized for GRAYSCALE images.
    """

    r_array1, g_array1, b_array1 = image1.bytes_to_channels()
    r_array2, g_array2, b_array2 = image2.bytes_to_channels()
    
    # Compute cosine similarity for each channel on a very small sample
    cosine_similarity_red = cosine_similarity(r_array1[:IMAGE_SAMPLE_SIZE], r_array2[:IMAGE_SAMPLE_SIZE])
    cosine_similarity_green = cosine_similarity(g_array1[:IMAGE_SAMPLE_SIZE], g_array2[:IMAGE_SAMPLE_SIZE])
    cosine_similarity_blue = cosine_similarity(b_array1[:IMAGE_SAMPLE_SIZE], b_array2[:IMAGE_SAMPLE_SIZE])

    # Get the average cosine similarity across all channels
    avg_cosine_similarity = (cosine_similarity_red + \
                             cosine_similarity_green + \
                             cosine_similarity_blue) / 3
    return avg_cosine_similarity


def cosine_similarity(array1, array2):
    # compute the cosine of the angle between the images in a n-dimensional space. This function needs to be more dynamic to accomodate for different sized arrays. 
    array1 = np.asarray(array1, dtype='uint32')
    array2 = np.asarray(array2, dtype='uint32')
    
    '''
    # Pad the smaller array to plot the image in the higher dimensional space. 
    pad_len_array1 = max(0, array2.shape[0] - array1.shape[0])
    pad_len_array2 = max(0, array1.shape[0] - array2.shape[0])
    padded_array1 = np.pad(array1, (0, pad_len_array1), mode='constant', constant_values=(0,0))
    padded_array2 = np.pad(array2, (0, pad_len_array2), mode='constant', constant_values=(0,0))

    dot_product = np.dot(padded_array1, padded_array2)
    '''

    dot_product = np.dot(array1, array2)

    # Compute frobenius norms
    magnitude1 = np.linalg.norm(array1)
    magnitude2 = np.linalg.norm(array2)
    
    # Compute cosine similarity
    similarity = dot_product / (magnitude1 * magnitude2)
    return similarity