# <p align="center" style="font-size: 60px;"><strong>Velib Cycling Stations Monitoring</strong> </p> 

[Overview] | [JCDecaux API Documentation] | [Architecture] | [Running the Application] | [Deployment] |




# 🔗 Overview

In Europe, strategically positioned bicycle stations, each with a designated bike capacity, require continuous monitoring for prompt identification of instances when a station becomes empty. Proactive measures are essential to maintain user satisfaction, as individuals expecting available bicycles rely on well-stocked stations. This project focuses on real-time visualizations, retrieving data from the JCDecaux API, and presenting it in a dynamic dashboard to achieve efficient monitoring and response.




## 🔗JCDecaux API Documentation
To obtain current information on bicycle stations, this project leverages the JCDecaux API. Detailed documentation for the API can be found at the [JCDecaux API Documentation.](https://developer.jcdecaux.com/#/home)

### Note:
Before using the JCDecaux API, make sure to obtain your API key from JCDecaux. You can register for an API key on their developer portal.

The JCDecaux API allows you to access information about bike stations, available bikes, and more, enabling dynamic and up-to-date visualizations in the project's dashboard.
## 🔗 Technologies & Architecture

Below is an architecture diagram illustrating the flow of data and the integration of technologies in this project:
![Architecture](/media/pipeline.png)

Each tool serves a distinct functionality in the data processing pipeline:
\textbf{Kafka (Version 3.3):} Manages data ingestion by fetching real-time data from the JCDecaux API and producing it to a Kafka topic named 'velo.'

- **Kafka (Version 3.3):** Manages data ingestion by fetching real-time data from the JCDecaux API and producing it to a Kafka topic named 'velo.'

- **Pyspark (Version 1.16.3):** Handles data processing by consuming data from the Kafka topic, executing processing tasks, and generating meaningful insights.

- **Elasticsearch (Version 7.17):** Acts as a data storage solution, storing the processed data in an index named 'bike.'

- **Kibana:** Provides visualization capabilities by being integrated with Elasticsearch, enabling dynamic visualization of the processed data.

The dockerization step has been implemented to enhance scalability, simplify installation, and facilitate easy access to the entire system.

## 🔗 Setup


#### 1-  Prerequisites:
- Ensure you have Docker installed on your machine.
- Obtain the necessary API key from JCDecaux for data retrieval.

#### 2-  Clone the Repository:

    - git clone https://github.com/Aymen568/Stations_monitoring.git

#### 3- Build the images and run the application:

    - docker-compose build
    - docker-compose up -d

Now all the required technologies are set up in Docker containers, eliminating the need for manual installation on your local machine.

#### 4-Access Kibana Dashboard:
Open your browser and go to http://localhost:5601 to access the Kibana dashboard.
All visualizations are preconfigured and will load automatically.
            
![Architecture](/media/map2.png)          
![Architecture](/media/pie.png)    
![Architecture](/media/courba1.png)  

#### 5-Stop the Application::

To stop the application and free up resources, run:

    - docker-compose down
