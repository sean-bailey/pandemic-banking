# pandemic-banking
This repo will hold the code and relevant materials for the McKinsey 2020 Hackathon for COVID-19

Endpoint:
https://hdb95y7ltk.execute-api.us-east-1.amazonaws.com/pandemic-demo

the following JSON can be provided to the REST API Endpoint:

​
{
“bucketName”: “pandemic-banking-demo”,
“fileName”: “20.png”,
“threshold”: “10",
“proximityThreshold”: “0.2"
}

note that there are currently 21 images in the bucket, selected with various levels of concentrations, from high density /high count to low density /high count to high density / low count to low density / low count
you can select the images by iterating from 1 through 21.png (edited)
for an example of a working API link:
https://hdb95y7ltk.execute-api.us-east-1.amazonaws.com/pandemic-demo?bucketName=pandemic-banking-demo&fileName=8.png&threshold=10&proximityThreshold=0.2 (edited)
I have it tied to an SNS topic, which, when the image exceeds the threshold or the proximityThreshold , sends an e-mail and a text message to myself (currently) and provides a quick message (too concentrated / too many people) and a link to the image.
I’m going to sign off for the night for now, but I can provide a simple S3 static website which allows for a simple button which triggers that API

You will get one of three successCodes, 0, 1 or 2. 0 means that there are no problems, 1 means that there are too many people detected in the image, 2 means that the concentration of people is too high (too many people not 2m apart)
