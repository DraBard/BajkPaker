deployment

gcloud run deploy product-service \                                                  
  --image "gcr.io/bajkpaker/product-service:v1" \
  --platform "managed" \
  --region "europe-central2" \
  --add-cloudsql-instances "bajkpaker:europe-central2:bajkpaker-db" \
  --set-env-vars "DATABASE_URL=mysql+asyncmy://root:BajkPaker33@/bajkpaker_dev?unix_socket=/cloudsql/bajkpaker:europe-central2:bajkpaker-db" \
  --port 8001

  docker push gcr.io/bajkpaker/product-service:v1