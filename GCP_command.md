# deployment

## Backend
#### Launch from backend dir
docker build --platform linux/amd64 -t gcr.io/bajkpaker/product-service:v1 -f services/product_service/Dockerfile .
docker push gcr.io/bajkpaker/product-service:v1

gcloud run deploy product-service \
--image "gcr.io/bajkpaker/product-service:v1" \
--platform "managed" \
--region "europe-central2" \
--add-cloudsql-instances "bajkpaker:europe-central2:bajkpaker-db" \
--set-env-vars "DATABASE_URL=mysql+asyncmy://root:BajkPaker33@/bajkpaker_dev?unix_socket=/cloudsql/bajkpaker:europe-central2:bajkpaker-db" \
--port 8001


docker build --platform linux/amd64 -t gcr.io/bajkpaker/order-service:v1 -f services/order_service/Dockerfile .
docker push gcr.io/bajkpaker/order-service:v1

gcloud run deploy order-service \
--image "gcr.io/bajkpaker/order-service:v1" \
--platform "managed" \
--region "europe-central2" \
--add-cloudsql-instances "bajkpaker:europe-central2:bajkpaker-db" \
--set-env-vars "DATABASE_URL=mysql+asyncmy://root:BajkPaker33@/bajkpaker_dev?unix_socket=/cloudsql/bajkpaker:europe-central2:bajkpaker-db" \
--port 8002


docker build --platform linux/amd64 -t gcr.io/bajkpaker/user-service:v1 -f services/user_service/Dockerfile .
docker push gcr.io/bajkpaker/user-service:v1

gcloud run deploy user-service \
--image "gcr.io/bajkpaker/user-service:v1" \
--platform "managed" \
--region "europe-central2" \
--add-cloudsql-instances "bajkpaker:europe-central2:bajkpaker-db" \
--set-env-vars "DATABASE_URL=mysql+asyncmy://root:BajkPaker33@/bajkpaker_dev?unix_socket=/cloudsql/bajkpaker:europe-central2:bajkpaker-db" \
--port 8003

## Frontend

docker build --platform linux/amd64 -t gcr.io/bajkpaker/frontend:v1 .
docker push gcr.io/bajkpaker/frontend:v1

gcloud run deploy frontend \
--image "gcr.io/bajkpaker/frontend:v1" \
--platform "managed" \
--region "europe-central2" \
--port 3000