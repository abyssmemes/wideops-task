
import os
import tempfile
import pymongo 
import datetime


from google.cloud import storage, vision
from wand.image import Image

storage_client = storage.Client()
vision_client = vision.ImageAnnotatorClient()

def safe_offensive_images(data):
    file_data = data

    file_name = file_data["name"]
    bucket_name = file_data["bucket"]

    blob = storage_client.bucket(bucket_name).get_blob(file_name)
    blob_uri = f"gs://{bucket_name}/{file_name}"
    blob_source = vision.Image(source=vision.ImageSource(image_uri=blob_uri))

    print(f"Analyzing {file_name}.")

    result = vision_client.safe_search_detection(image=blob_source)
    detected = result.safe_search_annotation
    score = detected.violence

    client = pymongo.MongoClient("mongodb+srv://image:image@clustermdb.i8cxm.mongodb.net/ClusterMDB?retryWrites=true&w=majority")
    db = client.test
    collection = db.test_collection
    post = {"image": file_name,
            "score": score,
            "date": datetime.datetime.utcnow()}
    posts = db.posts
    post_id = posts.insert_one(post).inserted_id

    client.close();
    # Process image
    if detected.violence == 5:
        print(f"The image {file_name} was detected as inappropriate.")
    else:
        print(f"The image {file_name} was detected as OK.") #!!!!!!
        return __save_image(blob)




def __save_image(current_blob):
    file_name = current_blob.name
    _, temp_local_filename = tempfile.mkstemp()

    # Download file from bucket.
    current_blob.download_to_filename(temp_local_filename)
    print(f"Image {file_name} was downloaded to {temp_local_filename}.")

    with Image(filename=temp_local_filename) as image:
        image.save(filename=temp_local_filename)

    safe_bucket_name = os.getenv("SAFE_BUCKET_NAME")
    safe_bucket = storage_client.bucket(safe_bucket_name)
    new_blob = safe_bucket.blob(file_name)
    new_blob.upload_from_filename(temp_local_filename)
    print(f"Safe image uploaded to: gs://{safe_bucket_name}/{file_name}")

    # Delete the temporary file.
    os.remove(temp_local_filename)


