# Preprocessing 🏭

The service is responsible for (pre-)processing all building data available to ADEPT.

## Requirements

+ Python ≥ 3.10
+ All packages from requirements.txt

## Development

### Local

Install dependencies from requirements.txt

Start the service:

```sh
uvicorn main:app --reload
```

### Docker

We provide a docker-compose in the root directory of ADEPT to start all services bundled together.


### Adding functionality

Please refer to the section
on [adding functionality](https://github.com/Adept-ML/Data-Management/tree/main#adding-functionality) in the
Data-Management-Service, as this service is directly dependent on it.

Copyright © ADEPT ML, TU Dortmund 2023