import json
import re
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize


class TextPreprocessor:
    def __init__(self, contractions_path=None, custom_stopwords_list=None, words_to_keep=None):
        if words_to_keep is None:
            words_to_keep = ['not']
        self.words_to_keep = set(words_to_keep)

        # 定义默认的停用词列表
        if custom_stopwords_list is None:
            custom_stopwords_list = [
                'be', 'am', 'are', 'is', 'and', 'who', 'in', 'at', 'alexand', 'how', 'to', 'as', 'a', 'an', 'the',
                'of', 'for', 'it', 'my', 'do', 'did', 'then', 'that', 'this', 'those', 'html', 'will', 'would',
                'bayesian', 'andrew', 'android', 'we', 'greek', 'js', 'astrobiolog', 'astronomi', 'ableton', 'api',
                'benchmark', 'angular', 'ancient', 'arduino', 'about', 'algo', 'bootstrap', 'buddhism', 'adam',
                'ajax', 'algebra', 'anyon', 'algorithm', 'if', 'i', 'you', 'capston', 'camp', 'caption', 'car',
                'card', 'care', 'camera', 'campaign', 'captur', 'america', 'american', 'web', 'all'
            ]

        # 初始化停用词列表，去除其中包含的保留词
        self.stop_words = set(custom_stopwords_list).difference(self.words_to_keep)

        self.lemmatizer = WordNetLemmatizer()

        # 加载和处理缩写词典
        if contractions_path is not None:
            with open(contractions_path, 'r') as file:
                self.contractions = json.load(file)
                self.contractions = {k.lower(): v.lower() for k, v in self.contractions.items()}
        else:
            self.contractions = {}

    def replace_contractions(self, text):
        return ' '.join([self.contractions.get(word, word) for word in text.split()])

    def preprocess_text(self, text):
        text = text.lower()
        text = self.replace_contractions(text)
        text = re.sub(r'[^a-z0-9\s\?!]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        tokens = word_tokenize(text)
        lemmatized_tokens = [self.lemmatizer.lemmatize(token) for token in tokens]
        filtered_tokens = [word for word in lemmatized_tokens if word not in self.stop_words]
        return ' '.join(filtered_tokens)
