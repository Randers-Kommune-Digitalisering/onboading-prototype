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

https://github.com/Randers-Kommune-Digitalisering/kithosting-randers-kommune-apps/blob/0bc3600ccc8ac97a9a1dcb4de6be0dcde0b4e79a/onboarding/values.yaml#L102

    extraVolumes:
      onboarding-data-volume: |
        persistentVolumeClaim:
          claimName: onboarding-data-volume
  podSecurityContext:

  i henhold til issue #215 skal det lige vurderes om det skal skiftes til database s3 eller ligenne
