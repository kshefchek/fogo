from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten,\
    GRU, LSTM, Conv2D, Conv1D, GlobalMaxPool1D
from keras.layers.embeddings import Embedding
from keras.optimizers import SGD
import numpy
from keras.callbacks import ModelCheckpoint, ReduceLROnPlateau
from random import shuffle
from math import floor

#class_fh = open('./label-map.txt', 'w')
#label_id = 0
#label_map = {}
#labels = []

#with open("./output/labels.txt", 'r') as label_file:
#    for line in label_file:
#        label = line.rstrip("\n")
#        if label not in label_map:
#            label_map[label] = label_id
#            class_fh.write("{}\n".format(label))
#            label_id += 1
#        labels.append(label_map[label])

#class_fh.close()
#labels = numpy.array(labels, dtype=numpy.uint32)

#BATCH_NUM = 2
BATCH_SIZE = 64

#total_samples = 600
#npy_rows = floor(total_samples/BATCH_NUM)
#last_rows = floor(total_samples/BATCH_NUM) + total_samples % BATCH_NUM

#steps_per_epoch = (BATCH_NUM-1)*floor(npy_rows/BATCH_SIZE) + floor(last_rows/BATCH_SIZE)

"""
def data_generator(labels, npz_file, batch_num, epochs):
    training_data_files = numpy.load(npz_file)
    random_order_batches = []
    batch_sequence = [i for i in range(1, batch_num+1)]
    for epoch in range(epochs):
        shuffled_copy = batch_sequence.copy()
        shuffle(shuffled_copy)
        random_order_batches.append(shuffled_copy)

    for epoch in random_order_batches:
        for batch in epoch:
            data = training_data_files["batch_{}".format(batch)]
            rows = data.shape[0]
            y_start = (batch - 1) * npy_rows
            label_chunk = labels[y_start:(y_start + rows)]

            data_batches = floor(rows/BATCH_SIZE)

            perm = numpy.random.permutation(len(label_chunk))
            label_chunk = label_chunk[perm]
            data = data[perm]
            perm = None
            x_batch = numpy.array_split(data, data_batches)
            y_batch = numpy.array_split(label_chunk, data_batches)
            data = None
            label_chunk = None
            for idx, val in enumerate(y_batch):
                yield (x_batch[idx], y_batch[idx])
"""

test_data = numpy.load("./output/validation.npy")
test_labels = numpy.load("./output/validation-labels.npy")


#test_labels = []
#with open("./output/validation-labels.txt", 'r') as label_file:
#    for line in label_file:
#        label = line.rstrip("\n")
#        test_labels.append(label_map[label])
#test_labels = numpy.array(test_labels)

training_data = numpy.load("./output/go-encoded.npy")
training_labels = numpy.load("./output/labels.npy")

#print(len(label_map.keys()))

model = Sequential()

# There are 24173 GO terms in our input, with the max profile length being 1075
model.add(Embedding(24173, 300, input_length=1075))
model.add(Dropout(0.3))

#model.add(Flatten())

#model.add(Dense(50, activation='relu'))
#model.add(Dropout(0.3))

model.add(Dense(100, activation='relu'))
model.add(Dropout(0.5))

#model.add(Dense(len(label_map.keys()), activation='sigmoid'))
model.add(Flatten())

# Output neurons should be number of distinct labels (# phenotypes)
model.add(Dense(21, activation='sigmoid'))

model.summary()


# sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
model.compile(loss='binary_crossentropy',
              metrics=['accuracy'],
              optimizer='adam')

filepath="weights-improvement-{epoch:02d}-{val_accuracy:.2f}.h5"
checkpoint = ModelCheckpoint(filepath, monitor='val_accuracy', verbose=1, save_best_only=True, mode='max')
callbacks_list = [
    #ReduceLROnPlateau(),
    checkpoint]

#model.fit_generator(data_generator(labels, "training-data.npz", BATCH_NUM, epochs=5),
#                    epochs=5,
#                    steps_per_epoch=steps_per_epoch,
#                    use_multiprocessing=False,
#                    callbacks=callbacks_list,
#                    validation_data=(test_data, test_labels))

model.fit(
    training_data,
    training_labels,
    epochs=20,
    batch_size=BATCH_SIZE,
    callbacks=callbacks_list,
    validation_data=(test_data, test_labels)
)

# Save model
model.save("./final-model.h5")
