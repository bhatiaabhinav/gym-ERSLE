from baselines.ers.utils import FFNN, Model
import tensorflow as tf
# import numpy as np
import os

DIR_NAME = os.path.dirname(__file__)

SG_MODEL_FILENAME = "sg_travel_times_model"
SG_DATA_FILENAME = "sg_travel_times_data.csv"
INPUT_FEATURES = 4
OUTPUT_FEATURES = 4


def _train_model_from_csv(model: Model, filepath):
    raise NotImplementedError()


sess = tf.Session()
sg_travel_times_estimator = FFNN(sess, "sg_travel_time_estimator", [
                                 INPUT_FEATURES], "float32", [OUTPUT_FEATURES], [64, 64], use_ln=True)
model_file_path = os.path.join(DIR_NAME, SG_MODEL_FILENAME)
data_file_path = os.path.join(DIR_NAME, SG_DATA_FILENAME)
if os.path.exists(model_file_path):
    sg_travel_times_estimator.load(model_file_path)
    print("Loaded singapore travel times estimator model")
else:
    if os.path.exists(data_file_path):
        print("Training a fresh model for singapore travel times")
        _train_model_from_csv(sg_travel_times_estimator, data_file_path)
    else:
        # raise FileNotFoundError(
        #     "Need either model file or raw data file to estimate travel times")
        pass
