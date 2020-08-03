if [[ $1 == 7 ]]
then
        echo sleeping for 2.5 mins
	sleep 150
else
        echo running as usual
fi
aws ecr get-login-password --region ap-south-1 | sudo docker login --username AWS --password-stdin 020452232211.dkr.ecr.ap-south-1.amazonaws.com
sudo docker container kill $(sudo docker ps -f NAME=backend_liqr_manager_1 -q)
sudo docker pull 020452232211.dkr.ecr.ap-south-1.amazonaws.com/liqr_manager:latest
sudo docker-compose up -d manager
