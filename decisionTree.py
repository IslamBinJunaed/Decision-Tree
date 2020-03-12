from csv import reader
import random


def load_CSV_file(file_name):
    read_file = open(file_name)
    read_lines = reader(read_file)
    data_set = list(read_lines)
    # print(data_set)

    return data_set


def str2float(dataset, column):
    for row in dataset:
        row[column] = float(row[column].strip())


def shuffle_data(dataset):
    length = len(dataset)
    random.seed(30)
    for i in range(length):
        j = random.randint(1, length - 1)
        data = dataset[i]
        dataset[i] = dataset[j]
        dataset[j] = data
    return dataset


def train_test_split(data_set, index, k=10):
    data_set = shuffle_data(data_set)

    train = []
    test = []

    for i in range(len(data_set)):
        if i % k == index:
            test.append(data_set[i])
        else:
            train.append(data_set[i])
            
    return train, test


def feature_class_split(dataset):
    length = len(dataset)
    fea_len = len(dataset[0]) - 1
    #print(fea_len)
    x = []
    y = []
    for i in range(length):
        x.append(dataset[i][:-1])
        y.append(int(dataset[i][fea_len]))

    return x, y


if __name__ == '__main__':
    file_name = 'iris.csv'
    data_set = load_CSV_file(file_name)

    for i in range(len(data_set[0])):
        str2float(data_set, i)

    total_sample = len(data_set)
    k_cv = 10
    # print(k_cv)

    for i in range(k_cv):
        train, test = train_test_split(data_set, i, k=k_cv)

        X_tr, Y_tr = feature_class_split(train)
        X_te, Y_te = feature_class_split(test)
         print(Y_tr)
         print(Y_te)
