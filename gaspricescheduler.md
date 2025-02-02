Start the docker container

-- Build the image of the container
docker build -t gaspricescheduler .

-- Run the docker container
docker run -d --name gaspricescheduler --network teslamate_default --link teslamate-database-1 gaspricescheduler