import os
import tempfile
import glob

from google.cloud import storage, vision
from wand.image import Image


storage_client = storage.Client()
vision_client = vision.ImageAnnotatorClient()

def thumbnail_images(data):
    file_data = data

    file_name = file_data["name"]
    bucket_name = file_data["bucket"]

    blob = storage_client.bucket(bucket_name).get_blob(file_name)
    blob_uri = f"gs://{bucket_name}/{file_name}"
    blob_source = vision.Image(source=vision.ImageSource(image_uri=blob_uri))


    print(f"Analyzing {file_name}.")

    
    print(f"The image {file_name} was detected as OK.")
    __thumb_image(blob)


def __thumb_image(current_blob):
    file_name = current_blob.name
    _, temp_local_filename = tempfile.mkstemp()

    # Download file from bucket.
    current_blob.download_to_filename(temp_local_filename)
    print(f"Image {file_name} was downloaded to {temp_local_filename}.")


    with Image(filename=temp_local_filename) as image:
        # Clone the image in order to process
        with image.clone() as thumbnail:
        # Invoke thumbnail function with x as 50 and y as 50
            thumbnail.thumbnail(50, 50)
        # Save the image
            thumbnail.save(filename=temp_local_filename)

    print(f"Image {file_name} was thumbnailed.")

    thumbnail_bucket_name = os.getenv("thumbnail_bucket")
    thumbnail_bucket = storage_client.bucket(thumbnail_bucket_name)
    new_blob = thumbnail_bucket.blob(file_name)
    new_blob.upload_from_filename(temp_local_filename)
    print(f"Thumbnailed image uploaded to: gs://{thumbnail_bucket_name}/{file_name}")

    # Delete the temporary file.
    os.remove(temp_local_filename)
