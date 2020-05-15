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


You will get one of three successCodes, 0, 1 or 2. 0 means that there are no problems, 1 means that there are too many people detected in the image, 2 means that the concentration of people is too high (too many people not 2m apart) as well as a link to the image.

## Cloud Based Security Camera Social Distancing Analysis and Alert Tool

Admittedly, the name needs work.

This project uses AWS Rekognition, Lambda, API Gateway, SNS and S3 static hosting to create an off the shelf easy to use and deploy solution for assisting businesses in reducing risk due to crowd densities.

Ideally, we would have access to a feed from a camera source, however that would require direct access to the business security camera feeds in question. This project demonstrates the realities of leveraging off the shelf models and cloud based solutions with existing security camera infrastructure to handle the new world of Social Distancing.

For the purposes of this demonstration, it all starts with the S3 bucket.

*Deploy an S3 bucket* which you have permissions to upload and download files from. This will be your primary repository for your demonstration images.

*Now for the SNS Topic*: Create an SNS topic and add the appropriate endpoints of your choosing. I've leveraged e-mail in this case, which will be sufficient.

*Next, the Lambda Role*.

In your AWS Account, create a lambda role called `pandemic_banking_role`, and keep track of the bucket and the SNS topic ARN from before. Give it the following policy:

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "logs:*",
                "rekognition:*"
            ],
            "Resource": [
                "arn:aws:rekognition:*:*:project/*/*",
                "arn:aws:logs:*:*:log-group:*:log-stream:*"
            ]
        },
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": [
                "logs:GetLogRecord",
                "rekognition:DetectFaces",
                "rekognition:DetectText",
                "rekognition:StartCelebrityRecognition",
                "logs:GetLogDelivery",
                "logs:ListLogDeliveries",
                "rekognition:GetLabelDetection",
                "rekognition:GetTextDetection",
                "logs:DeleteResourcePolicy",
                "rekognition:StartFaceDetection",
                "rekognition:GetContentModeration",
                "logs:CancelExportTask",
                "logs:DeleteLogDelivery",
                "s3:HeadBucket",
                "logs:PutDestination",
                "logs:DescribeResourcePolicies",
                "rekognition:StartPersonTracking",
                "logs:DescribeDestinations",
                "logs:DescribeQueries",
                "rekognition:DetectLabels",
                "rekognition:StartContentModeration",
                "rekognition:GetCelebrityRecognition",
                "rekognition:StartTextDetection",
                "logs:PutDestinationPolicy",
                "rekognition:GetPersonTracking",
                "rekognition:DetectModerationLabels",
                "rekognition:GetFaceDetection",
                "rekognition:StartLabelDetection",
                "rekognition:RecognizeCelebrities",
                "logs:StopQuery",
                "logs:TestMetricFilter",
                "rekognition:CompareFaces",
                "logs:DeleteDestination",
                "rekognition:GetCelebrityInfo",
                "logs:CreateLogGroup",
                "logs:CreateLogDelivery",
                "logs:PutResourcePolicy",
                "logs:DescribeExportTasks",
                "logs:GetQueryResults",
                "rekognition:GetFaceSearch",
                "rekognition:DescribeProjects",
                "s3:ListAllMyBuckets",
                "logs:UpdateLogDelivery"
            ],
            "Resource": "*"
        },
        {
            "Sid": "VisualEditor2",
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "sns:Publish",
                "logs:*",
                "s3:ListBucket",
                "rekognition:*"
            ],
            "Resource": [
                "arn:aws:rekognition:*:*:project/*/version/*/*",
                "arn:aws:rekognition:*:*:collection/*",
                "arn:aws:rekognition:*:*:streamprocessor/*",
                "arn:aws:sns:*:136289114074:<YOUR SNS TOPIC>",
                "arn:aws:logs:*:*:log-group:*",
                "arn:aws:s3:::*/*",
                "arn:aws:s3:::<YOUR BUCKET>"
            ]
        }
    ]
}
```

Next, on to Lambda. On your local machine, ensure you have your appropriate AWS Credentials configured. Go to the `./density-counter` directory and run

```
mkvirtualenv density-counter --no-site-packages
workon density-counter
pip3 install python-lambda boto3 -U
```

In `event.json`, ensure that the bucket name is set to your bucket name. in `service.py` ensure that the SNS_ARN is set to your appropriate ARN.

From there you can then upload the sample images to your S3 bucket. Once done, you can then run

```
lambda invoke -v
```
and test your code locally. If you're satisfied with your local testing, simply run

```
lambda deploy
```
and python-lambda will do the rest.

*API Gateway*

Create a new REST API and name it however you wish. Create a new GET method, and give it authorization to your newly deployed Lambda function. Under `Integration Request`, go to `Mapping Templates` and add a new content type, and type in
`application/json`

Click on that, and input the following for the template:

```
{
  "bucketName": "$input.params('bucketName')",
  "fileName": "$input.params('fileName')",
  "threshold": "$input.params('threshold')",
  "proximityThreshold": "$input.params('proximityThreshold')"
}
```

Save, then go to Actions > Enable CORS. Finally, deploy the API and save the Endpoint.


*Static site*

Open up `index.html` and modify the following values:
Change `process_url` to your API endpoint from above, ensuring to end it with a `?`
Change `bucketname` to match your bucket name

Save, then upload the file to your bucket.

Change your bucket properties to enable Static Website Hosting, with `index.html` being your site. Go to permissions, and turn Off "block public access".
###*Warning: by doing so now anyone can get access to the files in your bucket. This is only to duplicate the demonstration here. DO NOT USE THIS IN A PRODUCTION ENVIRONMENT YOU DO NOT WISH TO SHARE WITH THE WORLD.*

Next, plug in the following Bucket Policy, taking heed of the warning above:

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::<YOUR BUCKET NAME>/*"
        }
    ]
}

```

And that's it! With luck, you will then be able to access your S3 static site and test out the demo! When you click the button, you should get a notification if your randomly selected image triggers one of your thresholds.



#Nuts and Bolts: How does it work?

This project demonstrates that you can quickly and easily deploy a population density alert tool with no infrastructure (as everything is serverless) and no model training, with everything working out of the box. However, while the tools exist to perform image Recognition as a service, the ability to determine if the identified people are too close together is not such a common feature.

That's where the math section of the Lambda function comes in. To start, it runs on two major assumptions: all persons identified are all the same exact height, and that they are average height (~5'4", or ~1.625m). As the CDC recommends a 6ft / 2m distance for social distancing, that average height was definitely "good enough" for further calculations.

Next, we know that in an optical standpoint, the size an object appears to be is directly proportionate to how far away it is from the viewer (https://en.wikipedia.org/wiki/Perspective_(graphical)#Linear_perspective) and that we wanted to have a simple system that would work with the simple camera systems available commercially, without equipped rangefinders or stereoscopic capabilities. To calculate the distance between two objects, we can leverage the Pythagorean theorem as in a linear grid we can easily calculate X and Y distances.

By combining the two and considering Thale's Theorem, we can give a rough estimate of the distance two objects of identical size are away from each other.

As an example, if you have an object in the foreground, and an identical object in the background, the background object will appear smaller by the proportion of how farther it is away from the foreground object. You can therefore apply the ratio of the apparent sizes of the objects iteratively and one of the objects apparent heights as a unit of distance to map a rough distance between the two objects.

This means that you can do a rough estimation of distance between foreground and background objects without knowing the exact distance between the viewer and one of the objects, which is "good enough" for estimation of social distancing. Basically, if the people are an apparent human length apart, they should be reasonably assumed to following guidelines.

The system then allows you to enter in a total threshold and a proximity threshold.

The total threshold triggers an alert if the total number of people counted in the image exceeds the given value. The proximity threshold triggers an alert if the ratio of social distancing risks to the entire population in the image exceeds a certain percentage. This is an important "fuzzy logic" number, as people in small groups may be related and part of the same family or party, or perhaps the image being analyzed has people passing each other quickly. This means that the triggers can be tuned to be more meaningful based on real world feedback and adapt to best fit the scenario.
