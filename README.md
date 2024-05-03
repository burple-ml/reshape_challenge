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
- cd to the repo directory, and run the docker command to build the image - `docker build -t <tag_name> .` and cross fingers
- once the build is complete, run - `docker run -d -p 80:80 <tag_name>`. 
  you can skip the -d to avoid the detached mode of running the container, that way you can see the stdout
- go to your browser and go to the url - `http://localhost:80/docs`. here you will be able to see the swagger documentation in the openapi specification
  for the api endpoints that server exposes. 

PS: to test the image crop, upload the image as guided by the swagger docs page. In the response body you will receive some html code. Please download that code to a .html file and open it in your browser. 
You will be able to see the cropped image directly in your browser. 