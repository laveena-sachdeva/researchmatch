#!/usr/bin/env python

# Copyright 2017, Google, Inc.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Using the classify_text method to find content categories of text files,
Then use the content category labels to compare text similarity.

For more information, see the tutorial page at
https://cloud.google.com/natural-language/docs/classify-text-tutorial.
"""

# [START language_classify_text_tutorial_imports]
import argparse
import os

from google.cloud import language
import numpy
import six
# [END language_classify_text_tutorial_imports]
from google.oauth2 import service_account

# [START language_classify_text_tutorial_classify]

def classify(text, verbose=True):
    """Classify the input text into categories. """
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "/home/ubuntu/Documents/ASU_classwork/sem2/CC/proj2/cc-first-web-project-41851f0b5745.json"
    language_client = language.LanguageServiceClient()

    document = language.types.Document(
        content=text,
        type=language.enums.Document.Type.PLAIN_TEXT)
    response = language_client.classify_text(document)
    categories = response.categories

    result = {}

    for category in categories:
        # Turn the categories into a dictionary of the form:
        # {category.name: category.confidence}, so that they can
        # be treated as a sparse vector.
        result[category.name] = category.confidence

    if verbose:
        print(text)
        for category in categories:
            print(u'=' * 20)
            print(u'{:<16}: {}'.format('category', category.name))
            print(u'{:<16}: {}'.format('confidence', category.confidence))

    return result
# [END language_classify_text_tutorial_classify]


# [START language_classify_text_tutorial_index]
def categorize(applicant_list):
    """Classify each text file in a directory and write
    the results to the index_file.
    """

    result = {}
    for entry in applicant_list:
        try:
            categories = classify(entry.skill_description, verbose=False)

            result[entry] = categories
        except Exception:
            print('Failed to process {}'.format(entry))

    return result
# [END language_classify_text_tutorial_index]


def split_labels(categories):
    """The category labels are of the form "/a/b/c" up to three levels,
    for example "/Computers & Electronics/Software", and these labels
    are used as keys in the categories dictionary, whose values are
    confidence scores.

    The split_labels function splits the keys into individual levels
    while duplicating the confidence score, which allows a natural
    boost in how we calculate similarity when more levels are in common.

    Example:
    If we have

    x = {"/a/b/c": 0.5}
    y = {"/a/b": 0.5}
    z = {"/a": 0.5}

    Then x and y are considered more similar than y and z.
    """
    _categories = {}
    for name, confidence in six.iteritems(categories):
        labels = [label for label in name.split('/') if label]
        for label in labels:
            _categories[label] = confidence

    return _categories


def similarity(categories1, categories2):
    """Cosine similarity of the categories treated as sparse vectors."""
    categories1 = split_labels(categories1)
    categories2 = split_labels(categories2)

    norm1 = numpy.linalg.norm(list(categories1.values()))
    norm2 = numpy.linalg.norm(list(categories2.values()))

    # Return the smallest possible similarity if either categories is empty.
    if norm1 == 0 or norm2 == 0:
        return 0.0

    # Compute the cosine similarity.
    dot = 0.0
    for label, confidence in six.iteritems(categories1):
        dot += confidence * categories2.get(label, 0.0)

    return dot / (norm1 * norm2)


# [START language_classify_text_tutorial_query]
def query(index,text):
    """Find the indexed files that are the most similar to
    the query text.
    """

    # Get the categories of the query text.
    query_categories = classify(text, verbose=False)
    print(query_categories)
    similarities = []
    for filename, categories in six.iteritems(index):
        similarities.append(
            (filename, similarity(query_categories, categories)))

    similarities = sorted(similarities, key=lambda p: p[1], reverse=True)

    print('=' * 20)
    print('Query: {}\n'.format(text))
    for category, confidence in six.iteritems(query_categories):
        print('\tCategory: {}, confidence: {}'.format(category, confidence))
    print('\nMost similar indexed texts:')
    for filename, sim in similarities:
        # if sim > 0.3:
        print('\tFilename: {}'.format(filename))
        print('\tSimilarity: {}'.format(sim))
        print('\n')

    return similarities
# [END language_classify_text_tutorial_query]


if __name__ == '__main__':
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "/home/ubuntu/Documents/ASU_classwork/sem2/CC/proj2/cc-first-web-project-41851f0b5745.json"