git pull

sudo docker container kill $(sudo docker ps -q)
sudo docker-compose up -d --build
