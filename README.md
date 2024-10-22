# Vue-Python-Tempplate
Template for vue and python projects

## Kørsel af Frontenden(Vue)
* CD hen til vue folder: ``` cd vue ```
* Installerer afhængigheder: ``` npm install ```
* Compile, hot reload og start frontenden: ``` npm run serve ```

## Kørsel af Bakcenden(Python)
* CD hen til python folder: ``` cd python\src ```
* Start applikationen: ``` python main.py ```


## Udviklings commands:
* Bygge docker image: ```docker build -t vue-python-template .```
* Kør container ud fra det image man byggede: ```docker run -p 8080:8080 vue-python-template```
* Lint: ```flake8 python/src tests --count --select=E9,F63,F7,F82 --show-source --statistics```
* Unit tests: ``` pytest ```


