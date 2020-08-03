if [[ $1 == 7 ]]
then
	echo not sleeping
else
	echo sleeping for 7
	sleep 7
fi
git pull
sudo docker container kill $(sudo docker ps -f NAME=relief_backend_1 -q)
sudo docker-compose up -d --build backend
sudo docker image prune -f
