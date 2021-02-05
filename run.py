from app import create_app
from config.app_config import DevelopmentConfig, ProductionConfig


application = create_app(config_object=DevelopmentConfig)


if __name__ == '__main__':
    application.run()