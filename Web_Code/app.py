from flask import Flask
from models import db

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:7851696@127.0.0.1/project'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = '123456'  # 设置一个安全的密钥

    db.init_app(app)

    from routes import configure_routes
    configure_routes(app)

    return app



if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
