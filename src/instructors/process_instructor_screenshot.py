import boto3
import requests
import time
import datetime
from google.cloud import vision
from google.cloud.vision import AnnotateImageResponse
import os
import io

def screen_shot_processing(db, start):
    results = db.get_all_instructors()
    for i in range(0, len(results)):
        r = results[i]
        instructor_id = r[0]
        screenshot_url = r[27]
        response = requests.get(screenshot_url)

        image_path = "instructor_snapshot/{}.{}".format(instructor_id, screenshot_url[-3:])
        file = open(image_path, "wb")
        file.write(response.content)
        file.close()

        # AWS Rekognition
        response_aws_detect_labels, response_aws_detect_text, response_aws_detect_faces = call_aws_rekognize(image_path)
        values = [
            instructor_id,
            str(response_aws_detect_labels),
            str(response_aws_detect_text),
            str(response_aws_detect_faces),
        ]
        db.insert_fact_instructor_thumbnail_aws_result(values)

        # Google Cloud Vision
        response_gcloud_vision = call_gcloud_vision(image_path)
        values = [
            instructor_id,
            response_gcloud_vision
        ]
        db.insert_fact_instructor_thumbnail_gcloud_result(values)

        end = time.time()
        print('Iteration %d, Process Time: %s' % (i, str(datetime.timedelta(seconds=(end - start)))))


def call_gcloud_vision(image_path):
    file_name = os.path.abspath(image_path)
    with io.open(file_name, 'rb') as image_file:
        content = image_file.read()

    client = vision.ImageAnnotatorClient()
    response = client.annotate_image({
        'image': {'content': content}
    })
    time.sleep(2)
    result = AnnotateImageResponse.to_json(response).replace('\n', '').replace(' ', '')
    return result


def call_aws_rekognize(photo):
    client = boto3.client('rekognition')

    with open(photo, 'rb') as image:
        response_aws_detect_labels = client.detect_labels(Image={'Bytes': image.read()})
    time.sleep(2)

    with open(photo, 'rb') as image:
        response_aws_detect_text = client.detect_text(Image={'Bytes': image.read()})
    time.sleep(2)

    with open(photo, 'rb') as image:
        response_aws_detect_faces = client.detect_faces(Image={'Bytes': image.read()}, Attributes=['ALL'])
    time.sleep(1)

    return response_aws_detect_labels, response_aws_detect_text, response_aws_detect_faces


