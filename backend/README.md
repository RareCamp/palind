# PALIND backend

Django app implementing the PALIND backend spec.

You can run the app using Docker or as a development environment.

# How to build and run demo server using Docker

    docker build . -t palind 
    docker run -p 8000:8000 palind 

Then, open a browser and visit [http://localhost:8000/dataset/1/upload-csv](http://localhost:8000/dataset/1/upload-csv)

## Admin site

Visit http://localhost:8000/admin with user `admin` and password `1234`.

# Run the app for development

First, create a virtual environment:

    python3 -m venv venv             # Create virtual environment
    . ./venv/bin/activate            # Activate it for this shell
    pip install -r requirements.txt  # Install requirements

Second, create a superuser who will be able to access the admin site:

    python manage.py createsuperuser

Initialize the database by running the migrations:

    python manage.py migrate

Now, you can run the local development server with:

    python manage.py runserver


Visit [localhost:8000](http://localhost:8000) to access the site and
[localhost:8000/admin](http://localhost:8000/admin) to access the admin site.

## Install and run Terraform on AWS CloudShell

    git clone https://github.com/tfutils/tfenv.git ~/.tfenv
    mkdir ~/bin
    ln -s ~/.tfenv/bin/* ~/bin/
    tfenv install 1.7.0
    tfenv use 1.7.0
    terraform --version

    # Copy main.tf

    terraform init

    terraform plan
    terraform apply

## How to initialize DB

1. Make RDS database publicly accessible
2. Modify the default VPC security group to allow inbound traffic from your IP address to the postgres port (5432)
3. Export the following variables:
```
export DJANGO_DB_PORT=5432
export DJANGO_DB_HOST=XXX.us-east-1.rds.amazonaws.com # The RDS endpoint
export DJANGO_DB_USER_PASSWORD='{"username": "postgres", "password": "XXX"}'  # The RDS master password from the Secrets Manager
```
4. Run `./manage.py runserver` and visit [localhost:8000](http://localhost:8000) to check that the connection is done correctly. You should not be able to log in because there is no user yet.
5. Run `./manage.py createsuperuser` and create a superuser to access the admin site.
6. Visit [localhost:8000/admin](http://localhost:8000/admin) and log in with the superuser credentials.
7. Create an organization and add the superuser to it.
8. Fill in the name and last name of the superuser.
9. Visit [app.palind.io/admin](https://app.palind.io/admin) and log in with the superuser credentials to check that you have access to the production site.
10. Download the `HumanDO.json` from [GitHub](https://github.com/DiseaseOntology/HumanDiseaseOntology/tree/main/src/ontology).
11. Run `./manage.py import_diseases HumanDO.json` to fill the database with the diseases.
12. Remove Inbound rule from the VPC > Security Group.
13. Make RDS database not publicly accessible.
