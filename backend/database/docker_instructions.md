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

  ### DEPLOYING

  flyctl apps create bajkpaker-mysql
  flyctl deploy --app bajkpaker-mysql

  #### To test connection on fly.io

  Create tunnel, because it is on HTTPS I need a local tunnel to create a proxy that can connect with db on fly.io
  Remember it has to be on separate terminal

  flyctl proxy 3306
    # Correct proxy command syntax:
  fly proxy 3306:3306 -a bajkpaker-mysql
  # Or alternative format:
  # flyctl proxy 3306:3306 --app bajkpaker-mysql

  Open new terminal and:

  mysql -h 127.0.0.1 -P 3306 -u bajkpaker -p

  for mariadb:
  mysql -h 127.0.0.1 -P 3306 -u bajkpaker -p --enable-cleartext-plugin

  SHOW DATABASES;
  USE bajkpaker_dev;
  SHOW TABLES;
  DESC table_name;




Prompt:
  In order to deploy this project on fly.io I have to do the following things.
  1. Launch @fly.toml frontend with command 'flyctl launch'
  2. Launch@fly.toml database with command 'flyctl launch'
  3. launch product-service @fly.toml with command 'flyctl launch'
  4. Then I have to upload the images on the product service volume using @upload_images_flyio.sh 
  5. Then open proxy on database with 'flyctl proxy 3306'
  6. Update the database@update_image_metadata.py 
  Create one script that will do it with only one launch. Remember each of these files has to be launched from a folder level terminal and they are in different directiores.
