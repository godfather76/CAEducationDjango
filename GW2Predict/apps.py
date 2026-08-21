import joblib
from django.apps import AppConfig
from os import path, environ
from django.conf import settings


class GW2PredictConfig(AppConfig):
    name = "GW2Predict"
    model_dict = {}

    def ready(self):
        if environ.get('RUN_MAIN'):
            from keras.models import load_model
            models = ('penny', 'luxury')
            days = ('3d', '7d', '30d')
            path_base = path.join(settings.BASE_DIR, "GW2Predict", "models")
            for model in models:
                for day in days:
                    this_model_path = path.join(path_base, f'{model}_model_{day}.keras')
                    this_preprocess_path = path.join(path_base, f'{model}_preprocess_{day}.joblib')
                    this_y_preprocess_path = path.join(path_base, f'{model}_y_preprocess_{day}.joblib')
                    if path.exists(this_model_path):
                        self.model_dict[f'{model}_{day}'] = {
                            'model': load_model(this_model_path),
                            'preprocess': joblib.load(this_preprocess_path),
                            'y_preprocess': joblib.load(this_y_preprocess_path)
                        }

            print("--- Keras models successfully cached into Django memory ---")
