mongo_setup = "aws"

if mongo_setup == "docker_local":
    MONGO_DB = "reliefo"
    MONGO_HOST = "mongodb://mongo:27017"
elif mongo_setup == "aws":
    MONGO_DB = "reliefo"
    MONGO_HOST = "mongodb://ec2-13-232-202-63.ap-south-1.compute.amazonaws.com:27017"
else:
    MONGO_DB = "reliefo"
    MONGO_HOST = "mongodb://localhost:27017"
