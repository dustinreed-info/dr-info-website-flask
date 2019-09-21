# Dustin Reed Info - Flask Website
Source code for www.dustinreed.info.  Built with Flask and Jinja2, packaged to be deployed to AWS Elastic Beanstalk.

## Requirements
If you are deploying to AWS Elastic Beanstalk, select Python as the Preconfigured Platform.
When configuring Beanstalk enviroment, select "Configure More Options" and assign it to a VPC that has a public subnet. Assign a public ip address.