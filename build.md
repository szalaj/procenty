python:3.8-slim (pandas przy alpine się wywala)


--
zbudowanie obrazu:

docker image build -t flask_docker . 

flask_docker to nazwa obrazu 

--
uruchomienie obrazu na porcie 5000

docker run -p 5000:5000 -d flask_docker

-- compose

docker-compose -f docker-compose.yml up -d --build

 docker-compose down -v

 docker-compose down --remove-orphans

--
cmd zeby wyslac do awsa image

aws lightsail push-container-image --service-name flask-service --label app_docker4 --image app_docker4

aws lightsail push-container-image --service-name flask-service --label flap3 --image flaskapp3

aws lightsail push-container-image --service-name flask-service --label nginx --image serwer



flask-service.flap3.16

flask-service.nginx.17

docker run -p 5000:5000 -d  --name web --network todo-app flaskapp3

docker run -p 80:80 -d --network todo-app --name nginx serwer


git tag -a v0.3 -m "super wersja 0.3"