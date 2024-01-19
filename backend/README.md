# CuresDev backend

Django app implementing the CuresDev backend spec.

You can run the app using Docker or as a development environment.

# How to build and run demo server using Docker

    docker build . -t curesdev
    docker run -p 8000:8000 curesdev

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
    terraform init
