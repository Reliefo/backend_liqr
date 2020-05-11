
sudo docker container kill $(sudo docker ps -f NAME=relief_react_1 -q)
sudo docker pull 020452232211.dkr.ecr.ap-south-1.amazonaws.com/liqr_react:latest
sudo docker-compose up -d react
