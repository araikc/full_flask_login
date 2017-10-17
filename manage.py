from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from commands.init_db import InitDbCommand
from app import app, db

migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)
manager.add_command('initdb', InitDbCommand)

if __name__ == '__main__':
    manager.run()