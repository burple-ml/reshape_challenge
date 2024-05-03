from fastapi import APIRouter, Depends, Query
from .services import validate_image, MAX_SIZE, ImageHandler, \
            compute_avg_cosine_similarity, validate_multiform_data
from fastapi.responses import HTMLResponse


router = APIRouter(prefix='/v1')


@router.post("/crop")
async def image_crop(image_data: dict = Depends(validate_image),
                     width: int = Query(..., description="Width of the image, has to be greater than 0 and less than 1000. Padding will be added in this dimension if your image is smaller", gt=0, le=1000), 
                     height: int = Query(..., description="Height of the image, has to be greater than 0 and less than 1000. Padding will be added in this dimension if your image is smaller", gt=0, le=1000)):

    # pass to controller
    cropped_image_data = ImageHandler(image_data=image_data['image_data'],
                                 width=width,
                                 height=height,
                                 content_type=image_data['content_type']).crop_center()
    # Generate HTML content with image tag
    html_content = f'<img src="data:image/png;base64,{cropped_image_data.decode()}" />'
    # Return HTML as response
    return HTMLResponse(content=html_content, status_code=200)

@router.post("/difference")
async def image_difference(image_list: list = Depends(validate_multiform_data)):
    """ this route accepts 2 images that you have to upload. 
        it accepts multiform data, and only accept image/png and image/jpeg for each
        form item. 

        Returns: 
        an average cosine similarity score on a small sample of the input images, 
        which is the first 10 pixel intensities on each channel (r,g,b)
        Due to some library constraints,
        that solves for divide by zero exceptions, perfect 1 is a hard 
    """
    image1 = ImageHandler(image_data=image_list[0]['image_data'],
                          width=0, height=0,
                          content_type=image_list[0]['content_type'])
    image2 = ImageHandler(image_data=image_list[1]['image_data'],
                          width=0, height=0,
                          content_type=image_list[1]['content_type'])
    difference = compute_avg_cosine_similarity(image1=image1, image2=image2)
    return {"average_cosine_similarity": difference}

@router.post("/hash")
async def image_hash(image_data: dict = Depends(validate_image)):
    hash_value = ImageHandler(image_data=image_data['image_data'],
                          width=0, height=0,
                          content_type=image_data['content_type']).compute_average_hash()
    return {'hash': hash_value}