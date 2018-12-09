# Genobase
These instructions assume you have (and know how to work) `python3.6`, `Docker`

##### Technologies
1. Docker containers
1. Python 3.6
1. Django
1. Postgres
1. S3 buckets/objects
1. RabbitMQ
1. Celery workers

##### General architecture (and process)
1. `Client` `POST` a `GeneParser` object to `API Server`.
   1. `API Server` contacts `S3` and retrieves a presigned URL for upload.
   1. `API Server` stores it in the `GeneParser` object and returns to client.
1. `Client` `PUT` a file in the `S3` presigned URL.
1. `Client` `POST` to `API Server` that the file was uploaded.
1. `API Server` creates `AsyncJob` and puts a task in the `RabbitMQ`.
1. `Worker` pulls job from `RabbitMQ` and begins processing.
   1. `Worker` downloads file in chunks from `S3` and processes each chunk separately.
   1. Once the `Worker` finds a DNA sequence it stores it in `Postgres`.
   1. When file is complete the worker builds a JSON from the stored DNA sequences and sends it to `S3`.
1. `Client` polls `AsyncJob` progress until completed.
1. `Client` `GET` `GeneParser`
   1. `API Server` contacts `S3` and retrieves a presigned URL for download. 
1. `Client` downloads file using presigned URL.

##### How to run the project
1. Create terminal and navigate to project folder.
1. `docker network create genobase_default`
1. `docker-compose -f data.yml up`
   1. This will bring up `Postgres`, `Minio` and `RabbitMQ`
1. Wait for the database to initialize...
1. Create terminal and navigate to project folder.
1. `docker-compose -f processors.yml up`
   1. This will bring up the `API server`, `Celery workers` and a `schema migrations server`.  
1. Create terminal and navigate to project folder.
   1. Run the test script: `python tests/test_full_flow.py`
   1. Navigate to `./downloads/` and see the results.

##### Key places to look at:
1. `./gene_parser/tasks.py`: The processor background job.
1. `./gene_parser/parsers.py`: The file text parsers.
1. `./downloads/`: Where the resulted parsers are.
1. `.tests/test_full_flow.py`: The test script.

##### Closing notes
1. Since objects are stored in the DB it's simple to create an API to retrieve them in different manners.
1. Code assumes genes are not repeating in the files.
1. Improvement idea: Shard file to multiple workers.
1. Improvement idea: Use S3 bucket notifications instead of the `file_uploaded` endpoint.
1. Improvement idea: Store file in S3 in parts instead of whole.
1. I'm using `python manage.py runserver` as the server for demo simplicity.
1. No Authentication layer or any security for simplicity.
1. If you want to reset everything just delete the `./data` folder.
