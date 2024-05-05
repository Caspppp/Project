from tensorflow.keras.models import load_model
from tensorflow.keras.layers import LSTM, Dense, Bidirectional, Dropout
from transformers import TFRobertaModel


custom_objects_dict = {
    'TFRobertaModel': TFRobertaModel,
    'Bidirectional': Bidirectional,
    'LSTM': LSTM
}

model = load_model('models/model.h5', custom_objects=custom_objects_dict)
print(model.summary())

input_shape = model.input_shape
print("Input shape:", input_shape)

def get_model():
    return model