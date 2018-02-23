ACCESS_KEY_ID = 'AKIAJ24L7ECEFV5YE4BA'
ACCESS_SECRET_KEY = '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'
BUCKET_NAME = 'photoprojectumn'

import boto3
from os import listdir
from botocore.client import Config

def list_directory_s3(directory=''):
    global ACCESS_KEY_ID
    global ACCESS_SECRET_KEY
    global BUCKET_NAME

    s3 = boto3.resource(
            's3',
            aws_access_key_id=ACCESS_KEY_ID,
            aws_secret_access_key=ACCESS_SECRET_KEY,
            config=Config(signature_version='s3v4')
        )

    bucket = s3.Bucket(BUCKET_NAME)
    datalist = []
    for o in bucket.objects.filter(Delimiter='/'+directory):
        if o.key.split('/')[-2] == directory:
            datalist.append(o.key)
    return datalist

def get_file_s3(filename):
    global ACCESS_KEY_ID
    global ACCESS_SECRET_KEY
    global BUCKET_NAME

    s3 = boto3.resource(
    's3',
    aws_access_key_id=ACCESS_KEY_ID,
    aws_secret_access_key=ACCESS_SECRET_KEY,
    config=Config(signature_version='s3v4')
    )
    try:
        # Image download
        s3.Bucket(BUCKET_NAME).download_file(filename, filename);
        return True
    except:
        return False


def send_file_s3(accessor, filename,directory=''):

    global ACCESS_KEY_ID
    global ACCESS_SECRET_KEY
    global BUCKET_NAME

    try:
        data = open(accessor, 'rb')

        s3 = boto3.resource(
            's3',
            aws_access_key_id=ACCESS_KEY_ID,
            aws_secret_access_key=ACCESS_SECRET_KEY,
            config=Config(signature_version='s3v4')
        )
        s3.Bucket(BUCKET_NAME).put_object(Key=directory+filename, Body=data)
        return True
    except:
        return False

def sync_pictures():

    global ACCESS_KEY_ID
    global ACCESS_SECRET_KEY
    global BUCKET_NAME

    y = [x.split('/')[-1] for x in list_directory_s3('pictures')]
    for x in listdir('pictures/'):
        if x in y:
            print 'Already Exists'
        else:
            data = open('../pictures/'+x, 'rb')

            s3 = boto3.resource(
                's3',
                aws_access_key_id=ACCESS_KEY_ID,
                aws_secret_access_key=ACCESS_SECRET_KEY,
                config=Config(signature_version='s3v4')
            )
            s3.Bucket(BUCKET_NAME).put_object(Key='pictures/'+x, Body=data)
            print ("Done")
#print list_directory_s3('pictures')
#print send_file_s3('test.jpg','pictures/')
#print get_file_s3('faces/01045887134_1.jpg')
sync_pictures()