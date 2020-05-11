git pull
sudo docker container kill $(sudo docker ps -f NAME=relief_backend_1 -q)
sudo docker-compose up -d --build backend
