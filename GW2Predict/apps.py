from django.apps import AppConfig
from os import path, environ
from django.conf import settings


class Gw2PredictConfig(AppConfig):
    name = "GW2Predict"
    model = None

    def ready(self):
        if environ.get('RUN_MAIN'):
            from keras.models import load_model
            model_path = path.join(settings.BASE_DIR, "GW2Predict", "models", 'model.keras')
            if path.exists(model_path):
                self.model = load_model(model_path)
                print("--- Keras model successfully cached into Django memory ---")