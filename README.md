# Docker Django API template

# Help

- Clone the repo:

```ruby
    git clone https://github.com/joamona/django-api-template.git
```

- Change to the project folder:
```ruby
    cd django-api-template
```
- Create the pgadmin folders:
```ruby
    Windows: pgadmin_create_folders_windows.bat
    Linux: ./pgadmin_create_folders_linux.sh
```
- Create the containers and start the services:
```ruby
    docker compose up
```
- Check the services:

    - pgadmin: http://localhost:8050
    - geoserver: http://localhost:8080
    - Django API: http://localhost:8000/apphelloworld/hello_world/

# Start developping
To avoid to install Pyhton and its dependencies in your computer, you can 
use the interpreter in the container. You can achieve this with Visual Studio Code (VS).

- Start the services: docker compose up.
- Open VS.
- Press Ctrl + Shift + p.
- Paste the following: Dev Containers: Attach to Running Container.
- Select the container *-djangoapi-1.
- A new VS code window is started.
- In the terminal, change to the folder /home/$username, where the source code is.
- Select the interpreter: Ctrl + Shift + p, and type python select interpreter, and select the interpreter inthe container. In this way VS will help you to code.
- Now, you can modify the source files, and create new Django apps from the VS connected to the container.
- To create a new app, in the terminal, in the VS connected to the container, type: 

    python manage.py startapp mynewapp




