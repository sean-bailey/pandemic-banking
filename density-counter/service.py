# -*- coding: utf-8 -*-
import boto3
import math
import json
import uuid
from random import randint
s3 = boto3.client('s3')
sns=boto3.client('sns')
SNS_ARN="arn:aws:sns:us-east-1:136289114074:human-density-topic"
rekognition=boto3.client('rekognition')
#dynamodb = boto3.client('dynamodb')
#dynamoDBTable="fillerDB"

def getlabels(bucket,key):
    labelresponse = rekognition.detect_labels(
    Image={
    'S3Object':{
    'Bucket':bucket,
    'Name':key
    }
    },
    MaxLabels=9001,
    MinConfidence=90.0
    )
    return labelresponse

#To determine the distance between people, we can use the average height of
#people, use the Y value in the image to handle the depth perception issue
#and then basically use that as a radius with a little bit of fuzzy math to
#get the magic 2m number. Basically, the average height for a human is 5'4",
#which is 1.625m. That's good enough!

#our response will include the bounding box, which provides Width, height, left
#and top positions, all in reference as a ratio of overall image width, and
#height.


def processImageInfo(labelresponse, totalthreshold, proximitythreshold):
    labeldict = {}
    #dynamodict={}
    #We need only to act if the label string is a person
    #We need to record that person's location as a bounding box, as well as
    #their height and width
    #we need to give that record of 4 points a uuid
    #once all are recorded, we then need to perform appropriate "collision"
    #detections based on the math for the distance of the person
    #we also need to count the number of persons, easy
    #if at least 20% of the population has "collisions" an alert will trigger
    #and if the total population exceeds the threshold, an alert will trigger.
    print(labelresponse)
    for label in labelresponse['Labels']:
        for instance in label['Instances']:
            if "PERSON" in str(label['Name']).upper() :
                #so we know it's a person
                person_id = str(uuid.uuid4())
                top = float(instance['BoundingBox']['Top'])
                left = float(instance['BoundingBox']['Left'])
                height = float(instance['BoundingBox']['Height'])
                width= float(instance['BoundingBox']['Width'])
                right = left + width
                bottom = top + height
                #just in case we'd like to store the data...
                #dynamodict[personid] = {"L":[{"N":str(top)},{"N":str(bottom)},{"N":str(left)},{"N":str(right)},{"N":str(height)},{"N":str(width)}]}
                labeldict[person_id]={"top":top,"left":left,"right":right,
                "bottom":bottom,"height":height,"width":width}
    total_people=0
    proximity_flags=0
    for person in labeldict:
        print(labeldict[person])
        total_people+=1
        #now we count the total people and then do the distance comparisons...

        for person2 in labeldict:
            #right of person to left of person2, left of person to right of
            #We compare the heights of person and person2, and apply
            #the proportions of height and width to the distance calculations
            #of where the people are in the image.
            '''
            example:
            person1 has a top of .75 and a left of .75, a height of .2, a width
            of a .1, thus a right of .85 and a bottom of .95

            person2 has a top of .33 and a left of .33, a height of .3, a width
            of .15, thus a right of .48 and a bottom of .63

            we can assume that the heights of all the people are equal (as that
            is our measuring stick)

            meaning that
            '''
            if person2 is not person:
                xratio=(labeldict[person2]['width'])/((labeldict[person]['width']))
                yratio=(labeldict[person2]['height'])/((labeldict[person]['height']))
                xcomparedict={person:labeldict[person]['left'],person2:labeldict[person2]['left']}
                ycomparedict={person:labeldict[person]['top'],person2:labeldict[person2]['top']}
                xdelta = abs(labeldict[person]['left']-labeldict[person2]['left'])+(labeldict[max(xcomparedict,key=xcomparedict.get)]["width"])/2
                ydelta = abs(labeldict[person]['top']-labeldict[person2]['top'])+(labeldict[min(ycomparedict,key=ycomparedict.get)]["height"])/2
                fullx = xratio*xdelta
                fully = yratio*ydelta
                fullx=fullx*fullx
                fully=fully*fully
                distance=fullx+fully
                distance=math.sqrt(distance)
                if distance < (yratio * labeldict[person]['height']):
                    proximity_flags += 1
    proximity_flags = proximity_flags/2 #because we'll get double detection
    print(proximity_flags)
    print(total_people)
    if total_people >totalthreshold:
        return 1
    elif float(proximity_flags)/float(total_people) > proximitythreshold:
        return 2
    else:
        return 0

##we will need a "presigned_url" function and an sns function

def messagegeneratorfunction(messagelevel):
    print(messagelevel)
    subject = ""
    message = ""
    if messagelevel == 2:
        subject = "Social Distancing Intervention Required"
        message = "Person density has exceeded CDC recommendations and social distancing intervention is required. See image: "
    elif messagelevel == 1:
        subject = "Total count of people exceeds threshold"
        message ="There are too many people detected in the given space, and intervention is required. See image: "
    else:
        subject ="This message shouldn't be sent"
        message = "this message shouldn't be sent"
    returnarray=[subject,message]
    return returnarray




def handler(event, context):
    #file_name = str(randint(1,11))+".png"
    #print(file_name)
    statuscode=200
    bucket_name=event.get('bucketName')
    file_name=event.get('fileName')
    threshold_value=int(event.get('threshold'))
    proximity_threshold=float(event.get('proximityThreshold'))
    total_labels = getlabels(bucket_name,file_name)
    image_process_value=processImageInfo(total_labels,threshold_value,proximity_threshold)
    bodydata=None
    presigned_url_link = s3.generate_presigned_url('get_object',
                                         Params={'Bucket':bucket_name,
                                                 'Key': file_name},
                                         ExpiresIn=3600)
    if not image_process_value == 0:
        message_array = messagegeneratorfunction(image_process_value)


        response = sns.publish(
        TopicArn=SNS_ARN,
        Message = message_array[1]+str(presigned_url_link),
        Subject = message_array[0]
        )


    bodydata= json.dumps({
            'returndata' : presigned_url_link,
            'successcode':str(image_process_value)
        })
    finalresponse={}
    finalresponse["headers"]={
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*'
    }
    finalresponse['statusCode']=statuscode
    finalresponse['body']=bodydata
    return finalresponse
