from fastapi import UploadFile, \
             File, HTTPException, Depends
import requests
from .models import MultiFormData
import cv2
import numpy as np
import base64

MAX_SIZE = 5000000  # 5 MB ish(for pepe's sake), should ideally be fettched from some config service, or maintained using database CRUD operations or s3, or a simple yaml file.
IMAGE_SAMPLE_SIZE = 10

async def validate_image(file: UploadFile = File(...)): 
    if file is None:
        raise HTTPException(status_code=400, detail="Either file or URL must be provided.")
    
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Only JPEG and PNG files allowed. Try another file.")  # https://www.youtube.com/watch?v=h06ZkqM_7qM
    
    content = await file.read()
    
    file_size = len(content)
    if file_size > MAX_SIZE:
        raise HTTPException(status_code=400, detail=f"Image size exceeds the maximum allowed size of {MAX_SIZE} bytes.")
    
    content_type = file.content_type.split('/')[1]  # needs to be made into a method
    return {"image_data": content, "content_type": content_type}

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
    return [await validate_image(file=file1), await validate_image(file=file2)]


class ImageHandler():
    def __init__(self, image_data: bytes, width: int, 
                 height: int, content_type: str) -> None:
        self.image_data = image_data
        self.width = width
        self.height = height
        self.image_type = content_type

    def crop_center(self):
        """
        Cropped image's byte object
        """
        # Convert file object to numpy array
        file_bytes = np.asarray(bytearray(self.image_data), dtype=np.uint8)
        # Read the image using OpenCV
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

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
        success, encoded_image = cv2.imencode('.'+self.image_type, cropped_img)  # Change '.jpg' to '.png' if needed
        if success:
            base64_encoded_image = base64.b64encode(encoded_image)
            return base64_encoded_image
        else: 
            HTTPException(status_code=500, detail="Internal Server Error")
    
    def bytes_to_channels(self):
        
        # Convert byte data to numpy array
        image_array = np.frombuffer(self.image_data, dtype=np.uint8)
        
        # Decode image using OpenCV
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        
        # Split image into color channels
        b, g, r = cv2.split(image)
        return r.flatten(), g.flatten(), b.flatten()


def compute_avg_cosine_similarity(image1: ImageHandler, image2: ImageHandler):
    """ 
        this function takes 2 images and extracts the 3 channels as a numpy array, 
        computes cosine similarity between each corresponding channel, and then averages over them.
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
    # Convert arrays to numpy arrays
    #array1 = np.array(array1)
    #array2 = np.array(array2)
   
    # Pad or truncate arrays to equal length
    '''max_len = max(len(array1), len(array2))
    pad_length_1 = max(0, max_len - len(array1))
    pad_length_2 = max(0, max_len - len(array2))
    array1 = np.pad(array1, (0, pad_length_1), mode='constant')
    array2 = np.pad(array2, (0, pad_length_2), mode='constant')
    '''

    # Compute dot product
    dot_product = np.dot(array1, array2)
    
    # Compute magnitudes
    magnitude1 = np.linalg.norm(array1)
    magnitude2 = np.linalg.norm(array2)
    
    # Compute cosine similarity
    similarity = dot_product / (magnitude1 * magnitude2)
    
    return similarity