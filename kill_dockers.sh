git pull
cd relief_customer/
git pull https://github.com/akshay-bizz/relief_customer/ master
cd ../

sudo docker container kill $(sudo docker ps -q)
sudo docker-compose up -d --build
