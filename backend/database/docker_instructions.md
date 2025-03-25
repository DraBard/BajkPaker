locally:

Password are passed during building and are set as build args in the dockerfile

docker build -t  bajkpaker-mysql \
  --build-arg DB_PASSWORD=BajkPaker93.83 \
  --build-arg DB_ROOT_PASSWORD=BajkPaker93.83 \
  .

docker run -d \
  -p 3306:3306 \
  bajkpaker-mysql                       -> To open the port locally, i.e. docker is on port 3306 and the local machine has to open port 3306 as well to access the webpage



passing the password to container probably not needed, only during building to set the password.

docker run -d \
  -p 3306:3306 \
  -e DB_PASSWORD=BajkPaker93.83 \
  -e DB_ROOT_PASSWORD=BajkPaker93.83 \
  bajkpaker-mysql      



  #### To test connection on fly.io

  Create tunnel, because it is on HTTPS I need a local tunnel to create a proxy that can connect with db on fly.io
  Remember it has to be on separate terminal

  flyctl proxy 3306

  Open new terminal and:

  mysql -h 127.0.0.1 -P 3306 -u bajkpaker -p

SHOW DATABASES;
USE bajkpaker_dev;
SHOW TABLES;
DESC table_name;
