# backend
Repo for CuresDev backend running on AWS

# How to build and run demo server using Docker

      docker build . -t curesdev
      docker run -p 8000:8000 curesdev

Then, open a browser and visit [http://localhost:8000/dataset/1/upload-csv](http://localhost:8000/dataset/1/upload-csv)

## Admin site

Visit http://localhost:8000/admin with user `admin` and password `1234`.
