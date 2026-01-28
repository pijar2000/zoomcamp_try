# Homework 2

By Pijar HM

This is my method to solve homework, the answer is not provided here, my answer provided only in zoomcamp homework submit form

## Question 1

#### Installing Kestra

- Run this

```bash
cd 02-workflow-orchestration
docker compose up -d
```

Kestra will be pulled in docker, based on docker yaml the we can acces on

- Keep in mind that this kestra also insttalling postgres on port 5432 of your pc

- If you want access the database, but your port 5432 is not empty (for example you have postgres installed on 5432, you should move it to another port) for me it's like this

```yaml
pgdatabase:
  image: postgres:18
  environment:
    POSTGRES_USER: root
    POSTGRES_PASSWORD: root
    POSTGRES_DB: ny_taxi
  ports:
    - "5442:5432" # host port 5442 → container port 5432
```

- Then, you can access in your localhost port of 5442 in dbeaver od pgadmin with database name `ny_taxi`

- After you done with your kestra set-up you shoul ingest the remaining data of `ny_taxi` from 2019 to 2021, you can modified the flow corresponding to your needs

- the flow name is `05_postgres_taxi.yaml` load the yaml to flow managament with create flow

<img width="565" height="300" alt="Screenshot 2026-01-28 235904" src="https://github.com/user-attachments/assets/df0ba42a-41b4-4e86-b7d2-7b640cd58dc4" />

- paste the code to flow code

- the important part for backfill is here

```yaml
variables:
  file: "{{inputs.taxi}}_tripdata_{{trigger.date | date('yyyy-MM')}}.csv"
  staging_table: "public.{{inputs.taxi}}_tripdata_staging"
  table: "public.{{inputs.taxi}}_tripdata"
  data: "{{outputs.extract.outputFiles[inputs.taxi ~ '_tripdata_' ~ (trigger.date | date('yyyy-MM')) ~ '.csv']}}"
```
- You will backfill (it means load the data from exact periode of time to one another), clict trigger then click backfill, fill it to 2019 to 2021 for green and yellow data

- The important think for question 1 is you shoul add bash command in flow code for detect what size it is in kestra folder hidden inside docker

``` yaml
  - id: extract
    type: io.kestra.plugin.scripts.shell.Commands
    outputFiles:
      - "*.csv"
    taskRunner:
      type: io.kestra.plugin.core.runner.Process
    commands:
      - wget -qO- https://github.com/DataTalksClub/nyc-tlc-data/releases/download/{{inputs.taxi}}/{{render(vars.file)}}.gz | gunzip > {{render(vars.file)}}
      - du -b {{render(vars.file)}} | awk '{printf "%.1f MiB\n", $1/1048576}'  # This is bash command to list and look for file size
```
- After that you should look onto the Gantt section, you will see the size of the file

<img width="1395" height="902" alt="image" src="https://github.com/user-attachments/assets/6f4f0dad-0fc0-4749-b5ec-f326f8dcfd55" />


## Question 2

