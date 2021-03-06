# coding:utf-8
# from IPython.display import SVG
import six
import numpy as np
from matplotlib import pyplot as plt
np.random.seed(13)
from keras import models
from keras import layers
# from ..base import BaseEstimator
from keras.utils.visualize_util import model_to_dot


class TimeseriesModel(object):

    def __init__(self, rows, cols, output_dim, model_type='LSTM'):
        self.model_type = model_type
        self.rows = rows
        self.cols = cols
        self.output_dim = output_dim

    def param_new(self, rows, cols, output_dim):
        self.rows = rows
        self.cols = cols
        self.output_dim = output_dim

    def data_transform(self, train, test):
        x_train = train['x'].reshape(train['x'].shape[0], self.rows, self.cols)
        x_test = test['x'].reshape(test['x'].shape[0], self.rows, self.cols)
        x_train = x_train.astype('float32')
        x_test = x_test.astype('float32')
        y_train = train['y']
        y_test = test['y']

        return x_train, y_train, x_test, y_test

    def build(self, rows, cols, output_dim, loss='binary_crossentropy', optimizer='adadelta', metrics='accuracy'):
        self.param_new(rows, cols, output_dim)

        self.model = models.Sequential()
        if self.model_type == 'LSTM':
            self.model.add(layers.LSTM(20, return_sequences=False, input_shape=(self.rows, self.cols)))
        elif self.model_type == 'GRU':
            self.model.add(layers.GRU(20, return_sequences=False, input_shape=(self.rows, self.cols)))
        elif self.model_type == 'SimpleRNN':
            self.model.add(layers.SimpleRNN(20, return_sequences=False, input_shape=(self.rows, self.cols)))
        else:
            NotImplementedError()
        self.model.add(layers.Dense(self.output_dim))
        self.model.add(layers.Activation('sigmoid'))

        self.model.compile(loss=loss,
                           optimizer=optimizer,
                           metrics=[metrics])

        # SVG(model_to_dot(model, show_shapes=True).create(prog='dot', format='svg'))

    def train(self, x_train, y_train, batch_size=50, epoch=200, validation_split=0.1):
        result = self.model.fit(x_train, y_train,
                                batch_size=batch_size,
                                nb_epoch=epoch,
                                validation_split=validation_split)

        return result

    def test(self, x_test, y_test):
        preds = self.model.predict(x_test)
        preds[preds >= 0.5] = 1
        preds[preds < 0.5] = 0
        acc_ls = []
        for i in six.moves.range(self.output_dim):
            pred = preds[:, i]
            ans = y_test[:, i]
            sum_, all_ = 0, 0
            for pred_, ans_ in zip(pred, ans):
                if abs(pred_ - ans_) == 0:
                    sum_ += 1.0
                all_ += 1.0
            acc_ls.append(sum_ / all_)

        acc_all, acc_sum, res = 0.0, 0.0, []
        for pred, y_test_ in zip(preds, y_test):
            res = pred == y_test_
            acc_sum += 1
            if res.all():
                acc_all += 1.0
        acc_all = acc_all / acc_sum

        return acc_ls, acc_all

    # todo: visualize functions are not suit for manny results
    def visualize_acc(self, result, epoch):
        x = range(epoch)
        plt.plot(x, result.history['acc'], label="train acc")
        plt.plot(x, result.history['val_acc'], label="val acc")
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        plt.show()

    def visualize_loss(self, result, epoch):
        x = range(epoch)
        plt.plot(x, result.history['loss'], label="train loss")
        plt.plot(x, result.history['val_loss'], label="val loss")
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        plt.show()

