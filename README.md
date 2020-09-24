# Flask Demo App
This app implements a simple post app using Flask.

It demonstrates the following features:
- Account Mangement
    - Authentication via OAuth2 (Google, Github)
    - Authorization with roles (admin / member)
- Database using SQLAlchemy and PostgreSQL
- Email and other async tasks via Celery 
- Stripe charge and subscriptions

The project structure leverages Flask blueprints.

To enable a smooth development process, everything is docker / docker-compose based.

## Getting Started
To start the application and view on `localhost:5050`
```
make build
make bootstrap
```

To run flask commands, first start the flask shell with
```
make shell
```
Once in the shell, you can run scripts from `/scripts/fake.py` to insert test users and posts into the database.

## Credits

The post app and account management structure is based on the [Flask Mega Tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world) and the associated [book](https://github.com/miguelgrinberg/flasky).

The stripe subscription is based on [Build a SaaS App](https://buildasaasappwithflask.com/) but modified majorly to use the official stripe javascript (example from [Pretty Printed](https://github.com/PrettyPrinted/youtube_video_code/tree/master/2020/06/12/) tutorial) vs. implementing credit card pages from scratch.