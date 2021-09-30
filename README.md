# wideops-task

Folder "image-proccessing" - image recognition

Folder "image-proccessing-dev" - make thumbnail of not violens images

Activate - need to put some image (.jpg) to input bucket

When an image hits the first bucket, a notification is triggered, which triggers a pub sub for the service with processing. The image is processed thanks to the google vision. Then it saves the title of the image with the rating for violence and the date in the Mongo database. Next, the image goes into a safe bucket, which triggers another pub sub service with a mechanism for creating thumbnails and sending them to the final bucket of thumbnails.
Logs can be viewed in Cloud Run services
