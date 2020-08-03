if [[ $1 == 7 ]]
then
        echo sleeping for 3 mins
	sleep 180
else
        echo running as usual
fi
aws ecr get-login-password --region ap-south-1 | sudo docker login --username AWS --password-stdin 020452232211.dkr.ecr.ap-south-1.amazonaws.com
sudo docker container kill $(sudo docker ps -f NAME=backend_liqr_react_1 -q)
sudo docker pull 020452232211.dkr.ecr.ap-south-1.amazonaws.com/liqr_react:latest
sudo docker-compose up -d react
