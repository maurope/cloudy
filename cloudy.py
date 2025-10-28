import warnings
warnings.filterwarnings('ignore')
import re
import pandas as pd
import string
import spacy
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from wordcloud import WordCloud, STOPWORDS
from collections import Counter
import matplotlib.pyplot as plt

csv_path = "./data/biofilia_spanish.csv"
original_data = pd.read_csv(csv_path, header=None)
original_data.columns = ["text"]

filter_data = original_data.copy()

print("Null rows:", filter_data.isnull().sum()[0])

#FUNCTIONS
#----------

def clean(text):
    # Convert to lowercase
    text = str(text).lower()

    # Remove text between brackets (e.g., tags)
    text = re.sub(r'\[.*?\]', '', text)

    # Remove URLs
    text = re.sub(r'https?://\S+|www\.\S+', '', text)

    # Remove HTML tags
    text = re.sub(r'<.*?>+', '', text)

    # Remove punctuation marks
    text = re.sub('[%s]' % re.escape(string.punctuation), '', text)

    # Remove line breaks
    text = re.sub(r'\n', ' ', text)

    # Remove words containing numbers
    text = re.sub(r'\w*\d\w*', '', text)

    # Remove emojis and special (non-ASCII) characters
    # text = re.sub(r'[^\x00-\x7F]+', '', text)

    # Remove extra spaces at the beginning and end
    text = text.strip()

    return text

filter_data["clean_text"] = filter_data["text"].apply(clean)


stopword_es = set(stopwords.words('spanish'))
nlp_es = spacy.load('es_core_news_sm')



def clean_with_stopwords_and_lemmatization(text):
    # Procesar el texto usando spaCy
    doc = nlp_es(text)
    # Eliminar stopwords y aplicar lematización
    lemmatized = [token.lemma_ for token in doc if token.text.lower() not in stopword_es]
    # Unir los tokens lematizados y eliminar espacios extra
    return " ".join(lemmatized).strip()


filter_data["lemmatized_clean_text"] = filter_data["clean_text"].apply(clean_with_stopwords_and_lemmatization)

# Mostrar ejemplos de texto limpio vrs texto limpio avanzado
filter_data[['text','clean_text', 'lemmatized_clean_text']].head(3)



# WORD CLOUD GENERATION

text = " ".join(review for review in filter_data["lemmatized_clean_text"])
wordcloud = WordCloud(stopwords=STOPWORDS, background_color="white", width=800, height=400).generate(text)

plt.figure(figsize=(15,10))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")

plt.savefig("./biofilia.jpg", format="jpg", dpi=300, bbox_inches="tight")


# WORD COUNT

all_words = " ".join(filter_data["lemmatized_clean_text"]).split()
word_frequencies = Counter(all_words)
word_frequencies_df = pd.DataFrame.from_dict(word_frequencies, orient='index', columns=['frequency'])
word_frequencies_df = word_frequencies_df.sort_values(by='frequency', ascending=False)
word_frequencies_df = word_frequencies_df.reset_index().rename(columns={'index': 'words'})
word_frequencies_df.to_csv('./output_biofilia.csv', index=False, encoding="utf-8")


# WORDS FREQUENCY PLOT
top_10_words = word_frequencies_df.head(10)
colors = ['darkgreen'] * 5 + ['lightblue'] * 5

# Create the bar chart
plt.figure(figsize=(12, 6))
plt.bar(top_10_words['words'], top_10_words['frequency'], color=colors)
plt.xlabel("Words")
plt.ylabel("Frequency")
plt.title("Top 10 Most Frequent Words")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()

# Guarda el gráfico en PNG y JPG
plt.savefig("./top_10_palabras_biofilia.png", dpi=300, bbox_inches="tight")

# Muestra el gráfico
plt.show()


print('Succesfully run!')