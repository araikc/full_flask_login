from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from commands.init_db import InitDbCommand
from myapp import application, db

migrate = Migrate(application, db)

manager = Manager(application)
manager.add_command('db', MigrateCommand)
manager.add_command('initdb', InitDbCommand)

if __name__ == '__main__':
    manager.run()
