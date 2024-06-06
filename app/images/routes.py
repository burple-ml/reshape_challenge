from fastapi import APIRouter, Depends, Query, Form, HTTPException
from .services import validate_image, MAX_SIZE, ImageHandler, \
            compute_avg_cosine_similarity, validate_multiform_data, get_db, \
            Session, get_image
from fastapi.responses import HTMLResponse
from .models import ImageCrop

router = APIRouter(prefix='/v1')


@router.post("/crop")
async def image_crop(image_data: dict = Depends(validate_image),
                     width: int = Form(default=100, description="Width of the image, has to be greater than 0 and less than 1000. \
                            Padding will be added in this dimension if your image is smaller. Defaults to 100", gt=0, le=1000), 
                     height: int = Form(default=100, description="Height of the image, has to be greater than 0 and less than 1000. \
                            Padding will be added in this dimension if your image is smaller. Defaults to 100", gt=0, le=1000), 
                     db: Session = Depends(get_db)):
    """ This route accepts a multipart/form-data body, and 2 query parameters width and height in pixels which should be int, which default to a value of 100.
        Metadata in each form field is expected. so please do specify type in form data.  Moreoever, the encoded content is also validated, 
        so it should be valid png or jpeg. no funny stuff. 
        Returns: 
        the cropped image embedded in html, so your browser can quickly render it. Please download the html and save it in a .html file and open it in your browswer to see the cropped image.
    """
    # pass to controller
    cropped_image_data = ImageHandler(image_data=image_data['image_data'],
                                 width=width,
                                 height=height,
                                 content_type=image_data['content_type']).crop_center()
    
    # log to db
    db_image_crop = ImageCrop(
        width=width,
        height=height,
        data=cropped_image_data.decode())
    db.add(db_image_crop)
    db.commit()
    #db.refresh(db_image_crop)
        
    print(cropped_image_data.decode())
    # Generate HTML content, should ideally be generated from templates in a views folder.
    html_content = f'<img src="data:image/{image_data["content_type"]};base64,{cropped_image_data.decode()}"/>'

    # Return HTML response
    return HTMLResponse(content=html_content, status_code=200)


@router.post("/difference")
async def image_difference(image_list: list = Depends(validate_multiform_data)):
    """ this route strictly accepts 2 images that you have to upload. 
        it accepts multipart/form-data data, and only accept image/png and image/jpeg for each
        form item. 

        Returns: 
        an average cosine similarity (across the 3 channels - R,G & B) on a small sample of the image. 
        produces the same result for grayscales as of now. 
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
    """ this route strictly accepts 1 image and computes a hash using - average hash.

        Returns: 
        returns the 32 bit hash of the image. 
    """

    hash_value = ImageHandler(image_data=image_data['image_data'],
                          width=0, height=0,
                          content_type=image_data['content_type']).compute_average_hash()
    return {'hash': hash_value}


@router.get("/images/{image_id}")
def read_image(image_id: int, db_session: Session = Depends(get_db)):
    db_image = get_image(db_session, image_id)
    if db_image is None:
        raise HTTPException(status_code=404, detail="Image not found")
    return db_image