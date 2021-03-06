import pickle
import json
import random
import tensorflow
import tflearn
import numpy
import nltk
from nltk.stem.lancaster import LancasterStemmer
stemmer = LancasterStemmer()


with open("dataset.json") as file:
    data = json.load(file)

try:
    with open("data.pickle", "rb") as f:
        words, labels, training, output = pickle.load(f)
except:
    words = []
    labels = []
    docs_x = []
    docs_y = []
    

    for purpose in data["purpose"]:
        for intent in purpose["intents"]:
            for pattern in intent["patterns"]:
                word_tokenized = nltk.word_tokenize(pattern)
                words.extend(word_tokenized)
                docs_x.append(word_tokenized)
                docs_y.append(intent["tag"])

            if intent["tag"] not in labels:
                labels.append(intent["tag"])

    words = [stemmer.stem(w.lower()) for w in words if w != "?"]
    words = sorted(list(set(words)))

    labels = sorted(labels)

    training = []
    output = []

    out_empty = [0 for _ in range(len(labels))]

    for x, doc in enumerate(docs_x):
        

        wrds = [stemmer.stem(w.lower()) for w in doc]

        for w in words:
            if w in wrds:
                bag.append(1)
            else:
                bag.append(0)

        output_row = out_empty[:]
        output_row[labels.index(docs_y[x])] = 1

        training.append(bag)
        output.append(output_row)

    training = numpy.array(training)
    output = numpy.array(output)

    with open("data.pickle", "wb") as f:
        pickle.dump((words, labels, training, output), f)

net = tflearn.input_data(shape=[None, len(training[0])])
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, len(output[0]), activation="softmax")
net = tflearn.regression(net)

model = tflearn.DNN(net)
try:
    model.load("model.tflearn")
except:
    model.fit(training, output, n_epoch=2000, batch_size=8, show_metric=True)
    model.save("model.tflearn")


def word_list(s, words):
    list = [0 for _ in range(len(words))]

    s_words = nltk.word_tokenize(s)
    s_words = [stemmer.stem(word.lower()) for word in s_words]

    for se in s_words:
        for i, w in enumerate(words):
            if w == se:
                list[i] = 1

    return numpy.array(list)


def chat():
    print("Start talking with the bot (type quit to stop)!")
    while True:
        inp = input("You: ")
        if inp.lower() == "quit":
            break

        results = model.predict([word_list(inp, words)])
        results_index = numpy.argmax(results)
        tag = labels[results_index]

        for purpose in data["purpose"]:
            for tg in purpose["intents"]:
                if tg['tag'] == tag:
                    responses = tg['responses']

        print(responses)


def api_chat(inp):
    results = model.predict([word_list(inp, words)])
    results_index = numpy.argmax(results)
    tag = labels[results_index]
    
    for purpose in data["purpose"]:
        for tg in purpose["intents"]:
            if tg['tag'] == tag:
                responses = tg['responses']

chat()
