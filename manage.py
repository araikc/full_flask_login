from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from myapp.commands.init_db import InitDbCommand
from myapp import app, db

migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)
manager.add_command('initdb', InitDbCommand)

if __name__ == '__main__':
    manager.run()
