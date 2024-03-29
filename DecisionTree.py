import numpy as np
import pandas as pd

import random
from pprint import pprint


def train_test_split(df, test_size):
    if isinstance(test_size, float):
        test_size = round(test_size * len(df))

    indices = df.index.tolist()
    test_indices = random.sample(population=indices, k=test_size)

    test_df = df.loc[test_indices]
    train_df = df.drop(test_indices)

    return train_df, test_df


def check_purity(data):
    label_column = data[:, -1]
    unique_classes = np.unique(label_column)

    if len(unique_classes) == 1:
        return True
    else:
        return False


def classify_data(data):
    label_column = data[:, -1]
    unique_classes, counts_unique_classes = np.unique(label_column, return_counts=True)

    index = counts_unique_classes.argmax()
    classification = unique_classes[index]

    return classification


def get_potential_splits(data):
    potential_splits = {}
    _, n_columns = data.shape
    for column_index in range(n_columns - 1):  # excluding the last column which is the label
        potential_splits[column_index] = []
        values = data[:, column_index]
        unique_values = np.unique(values)

        for index in range(len(unique_values)):
            if index != 0:
                current_value = unique_values[index]
                previous_value = unique_values[index - 1]
                potential_split = (current_value + previous_value) / 2

                potential_splits[column_index].append(potential_split)

    return potential_splits


def split_data(data, split_column, split_value):
    split_column_values = data[:, split_column]

    data_below = data[split_column_values <= split_value]
    data_above = data[split_column_values > split_value]

    return data_below, data_above


def calculate_entropy(data):
    label_column = data[:, -1]
    _, counts = np.unique(label_column, return_counts=True)

    probabilities = counts / counts.sum()
    entropy = sum(probabilities * -np.log2(probabilities))

    return entropy


def calculate_overall_entropy(data_below, data_above):
    n = len(data_below) + len(data_above)
    p_data_below = len(data_below) / n
    p_data_above = len(data_above) / n

    overall_entropy = (p_data_below * calculate_entropy(data_below)
                       + p_data_above * calculate_entropy(data_above))

    return overall_entropy


def determine_best_split(data, potential_splits):
    overall_entropy = 9999
    for column_index in potential_splits:
        for value in potential_splits[column_index]:
            data_below, data_above = split_data(data, split_column=column_index, split_value=value)
            current_overall_entropy = calculate_overall_entropy(data_below, data_above)

            if current_overall_entropy <= overall_entropy:
                overall_entropy = current_overall_entropy
                best_split_column = column_index
                best_split_value = value

    return best_split_column, best_split_value


# the structure of sub_tree
sub_tree = {"question": ["yes_answer",
                         "no_answer"]}

# the following line is just an example of how the tree will look like
example_tree = {"petal_width <= 0.8": ["Iris-setosa",
                                       {"petal_width <= 1.65": [{"petal_length <= 4.9": ["Iris-versicolor",
                                                                                         "Iris-virginica"]},
                                                                "Iris-virginica"]}]}


def classify_example(example, tree):
    question = list(tree.keys())[0]
    feature_name, comparison_operator, value = question.split()

    # ask question
    if example[feature_name] <= float(value):
        answer = tree[question][0]
    else:
        answer = tree[question][1]

    # base case
    if not isinstance(answer, dict):
        return answer

    # recursive part
    else:
        residual_tree = answer
        return classify_example(example, residual_tree)


def calculate_accuracy(test, tree):
    count = 0
    total = len(test)

    print('\n******************** testing ************************\n')
    print("\nActual          Predicted\n")

    for i in range(total):
        row = test.iloc[i]
        answer = classify_example(row, tree)

        if answer == row[-1]:
            count += 1
            print(row[-1], answer)
        else:
            print(row[-1], answer, " WRONG_AMSWER_DETECTED")

    return count / total


def get_confusion_matrix(test, tree):
    tp = tn = fp = fn = 0

    length = len(test)

    for i in range(length):
        row = test.iloc[i]
        answer = classify_example(row, tree)

        if answer == row[-1]:
            tp += 1
            # print(row[-1], answer)

        else:
            fn += 1
            # print(row[-1], answer, " WRONG_AMSWER_DETECTED")

    return tp, tn, fp, fn


def calculate_recall(tp, fn):
    recall = tp / (tp + fn)

    return recall


def calculate_precision(tp, fp):
    precision = tp / (tp + fp)

    return precision


def calculate_f_measure(recall, precision):
    f_measure = 2 * recall * precision / (recall + precision)

    return f_measure


def decision_tree_algorithm(df, counter=0, min_samples=2, max_depth=5):
    # data preparations
    if counter == 0:
        global COLUMN_HEADERS
        COLUMN_HEADERS = df.columns
        data = df.values
    else:
        data = df

    # base cases
    if (check_purity(data)) or (len(data) < min_samples) or (counter == max_depth):
        classification = classify_data(data)

        return classification


    # recursive part
    else:
        counter += 1

        # helper functions
        potential_splits = get_potential_splits(data)
        split_column, split_value = determine_best_split(data, potential_splits)
        data_below, data_above = split_data(data, split_column, split_value)

        # instantiate sub-tree
        feature_name = COLUMN_HEADERS[split_column]
        question = "{} <= {}".format(feature_name, split_value)
        sub_tree = {question: []}

        # find answers (recursion)
        yes_answer = decision_tree_algorithm(data_below, counter, min_samples, max_depth)
        no_answer = decision_tree_algorithm(data_above, counter, min_samples, max_depth)

        # If the answers are the same, then there is no point in asking the qestion.
        # This could happen when the data is classified even though it is not pure
        # yet (min_samples or max_depth base cases).
        if yes_answer == no_answer:
            sub_tree = yes_answer
        else:
            sub_tree[question].append(yes_answer)
            sub_tree[question].append(no_answer)

        return sub_tree


df = pd.read_csv('IRIS.csv')
df = df.rename(columns={"species": "label"})

# random.seed(0)
np.random.rand(0)
train_df, test_df = train_test_split(df, test_size=20)

data = train_df.values
# print(data[:5]) this is optional just  to see the first 5 rows of the dataset


tree = decision_tree_algorithm(train_df, max_depth=3)
print("\n\n------------------------- decision tree -------------------------\n\n")
pprint(tree)

# print(sub_tree)

example = test_df.iloc[0]
example

# print(classify_example(example, tree))


tp, tn, fp, fn = get_confusion_matrix(test_df, tree)

accuracy = calculate_accuracy(test_df, tree)
recall = calculate_recall(tp, fn)
precision = calculate_precision(tp, fp)
f_measure = calculate_f_measure(recall, precision)

print()
print("Accuracy: ", accuracy)
print("Recall: ", recall)
print("Precision: ", precision)
print("f measure: ", f_measure)
