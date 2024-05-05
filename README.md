# reshape_challenge
reshape interview challenge

## Introduction
This is a fastapi application that does some neat image processing and computes some image metrics for images
As of now 

## Releases 
-v1

## How to run and test the server:-

to run this server on your local machine and to test it in 4 simple steps:-
- clone this repo to your local machine.
- cd to the repo directory, and run the docker command to build the image - `docker build -t <repo:tag_name> .` and cross fingers
- once the build is complete, run - `docker run -d -p 80:80 <repo:tag_name>`. 
  you can skip the -d to avoid the detached mode of running the container, that way you can see the stdout
- go to your browser and go to the url - `http://localhost:80/docs`. here you will be able to see the swagger documentation in the openapi specification
  for the api endpoints that server exposes. 

PS: to test the image crop, upload the image as guided by the swagger docs page. In the response body you will receive some html code. Please download that code to a .html file and open it in your browser. 
You will be able to see the cropped image directly in your browser. 

## Answers and assumptions
#### Answers
- The metric I chose for signifying the differences in the pictures is the cosine similarity. The cosine similarity basically measures the cosine of the angle between 2 vectors in a n-dimensional space.
  It gives a neat number between 0 and 1, where 0 being lesser degree of similarity between the images, and 1 signifying that the images are similiar or a scalar multiple of the other.
  This is very cool because in the case of 1 we can even capture cases where images have been subjected to some linear transformation and we can catch that, simply by using this metric. 

  To compute the cosine similarity, I have converted the image to a 3d-numpy array of size \( m \times n \times c \). This numpy array, represents the pixel grid on the first 2 dimensions, where each element tells us the pixel intensity at 
  that location in the grid, and the third dimension is for each of the R,G,B channels. Each channel is treated as a vector in the \( m \times n \)-dimensional space, and then the cosine similarity is computed as 
  \[
  \text{Cosine Similarity}(A, B) = \frac{{A \cdot B}}{{\|A\| \cdot \|B\|}}
 \]  
  The above is computed on a small sample of the images, and for each channel and then averaged to give the final score.
- aHash (average Hash algorithm) is used to compute a hash that can uniquely identify the image. In the algorithm, the images are resized to a size 8x8 and a few more transformartions are applied to it, including grayscaling of the image, to produce 
  the hash. 
- OpenCV and Numpy were the libraries were used for most of the image processing and transformation.

#### Assumptions
the following assumptions were made during development
- Allowed to put max size on images. I have put a max size on the images at arround 5 MB.
- Default value for breadth and width added, if not specified explicitly by the client.
- I have added padding to the image, in case the breadth and width in the query parameters for the /crop route exceeds that dimension of the image.
- The image is embedded in the html response of the /crop route.  
- no authorization is required for using the routes, aka they are public.
- in writing the dockerfile, I have assumed that the repo is your pwd. 
- the images will be provided as binary data only, aka the images will be provided using a multipart/form-data body, with the correct MIME type specified on each form field. Thus, the user is not allowed to use binary data, and url at the same time. 

## Further Optimisations
- There could be more optimizations in the way the image difference metric is calculated, to not take a sample, but compute it on the whole image. This would require some optimisations. 
- Allow the user to input both url and binary data, and give preference. 