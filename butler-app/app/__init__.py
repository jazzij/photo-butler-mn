from flask import Flask

#initialize app
app = Flask(__name__, instance_relative_config=True)

#load view
#from app import views

app.config.from_object('config')
