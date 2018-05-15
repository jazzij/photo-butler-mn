# PhotoProject - Distributed (RasPi)

1. Replace MongoDB instance IP Address in mongocommands.py
2. Send Files to the Distributed Cluster by copying the images into Pictures directory and executing sendfiles.py
3. Initialize PhotoProject_distributed.py on each celery supported distributed instance with network connection to Mongo Instance.
4. Execute main controller to start a queue of distributed tasks on network.
5. Results are consolidated afer processing and are available in MongoDB results database.
