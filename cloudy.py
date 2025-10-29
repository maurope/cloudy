# Written by Mauricio Peñuela 
# https://github.com/maurope/cloudy

import warnings
warnings.filterwarnings('ignore')
import os
import sys
import re
import pandas as pd
import string
import spacy
import nltk
import matplotlib.pyplot as plt
from datetime import datetime
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from wordcloud import WordCloud, STOPWORDS
from collections import Counter


#-----------------------
# DATA LOAD
#-----------------------

if len(sys.argv) < 2:
    print("❌ Use: python cloudy.py <your_data.txt>")
    sys.exit(1)

path = sys.argv[1]

if not os.path.exists(path):
    print(f"❌ The file '{path}' do not exist.")
    sys.exit(1)

print(f"📂 Selected file: {path}")


#-----------------------
# LANGUAGE SELECTION
#-----------------------

print("")
print("Type 'en' for English / Escribe 'es' para español")


lang = input("🌐 language/idioma: ").strip().lower()

if lang not in ["es", "en", ""]:
    print("⚠️ Invalid language. Use 'en' for English or 'es' for Spanish.")
    print("⚠️ Idioma no válido. Usa 'en' para inglés o 'es' para español.")
    sys.exit(1)

if lang == "":
    lang = "en"  # idioma por defecto


#-----------------------
# SELECTED LANGUAGE SETTINGS
#-----------------------

if lang == "en":
    print("🔤 Analyzing in English...")
    stopwords = set(stopwords.words('english'))
    nlp = spacy.load('en_core_web_sm')
elif lang == "es":
    print("🔤 Analizando en Español...")
    stopwords = set(stopwords.words('spanish'))
    nlp = spacy.load('es_core_news_sm')


# --- Localized labels depending on lang ---
if lang == "es":
    labels = {
        "wordcloud_title": "Nube de palabras",
        "top_title": "Top 10 palabras más frecuentes",
        "xlabel": "Palabras",
        "ylabel": "Frecuencia",
        "words_col": "palabras",
        "frequency_col": "frecuencia",
        "saving_wordcloud": "✅ Nube de palabras guardada como",
        "saving_freq": "✅ Frecuencias guardadas en",
        "saving_chart": "✅ Gráfico guardado como",
        "output_folder": "Carpeta de salida creada:",
        "lang_suffix": "es"
    }
else:  # default 'en'
    labels = {
        "wordcloud_title": "Word Cloud",
        "top_title": "Top 10 most frequent words",
        "xlabel": "Words",
        "ylabel": "Frequency",
        "words_col": "words",
        "frequency_col": "frequency",
        "saving_wordcloud": "✅ Word cloud saved as",
        "saving_freq": "✅ Frequencies saved in",
        "saving_chart": "✅ Chart saved as",
        "output_folder": "Output folder created:",
        "lang_suffix": "en"
    }





#-----------------------
# OUTPUT FOLDER
#-----------------------

if not os.path.exists("output"):
    os.makedirs("output")
    print("📁 Output folder created.")
else:
    pass
    

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
basename = os.path.splitext(os.path.basename(path))[0]   # nombre del archivo sin ruta ni extensión
output_dir =  os.path.join("output", f"{timestamp}_{basename}")
os.makedirs(output_dir, exist_ok=True)
print(f"📁 Run folder created: {output_dir}")

# Output paths

lang_suffix = labels['lang_suffix']

wordcloud_path = os.path.join(output_dir, f"{basename}_{lang_suffix}.jpg")
word_frequencies_path = os.path.join(output_dir, f"{basename}_{lang_suffix}_frecuencies.csv")  # puedes poner _frequencies.csv si en inglés
top_chart_path = os.path.join(output_dir, f"{basename}_{lang_suffix}_top_10.jpg")




with open(path, 'r', encoding='utf-8') as f:
    lines = f.read().splitlines()

original_data = pd.DataFrame(lines, columns=['text'])

original_data.columns = ["text"]

filter_data = original_data.copy()

print("Null rows:", filter_data.isnull().sum()[0])

#-----------------------
#FUNCTIONS
#-----------------------

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



def clean_with_stopwords_and_lemmatization(text):
    # Procesar el texto usando spaCy
    doc = nlp(text)
    # Eliminar stopwords y aplicar lematización
    lemmatized = [token.lemma_ for token in doc if token.text.lower() not in stopwords]
    # Unir los tokens lematizados y eliminar espacios extra
    return " ".join(lemmatized).strip()


filter_data["lemmatized_clean_text"] = filter_data["clean_text"].apply(clean_with_stopwords_and_lemmatization)

# Mostrar ejemplos de texto limpio vrs texto limpio avanzado
filter_data[['text','clean_text', 'lemmatized_clean_text']].head(3)


#-----------------------
# WORD CLOUD GENERATION
#-----------------------

text = " ".join(review for review in filter_data["lemmatized_clean_text"])
wordcloud = WordCloud(stopwords=STOPWORDS, background_color="white", width=800, height=400).generate(text)

plt.figure(figsize=(15,10))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")

plt.savefig(wordcloud_path, format="jpg", dpi=300, bbox_inches="tight")

#-----------------------
# WORD COUNT
#-----------------------

all_words = " ".join(filter_data["lemmatized_clean_text"]).split()
word_frequencies = Counter(all_words)
word_frequencies_df = pd.DataFrame.from_dict(word_frequencies, orient='index', columns=[labels['frequency_col']])
word_frequencies_df = word_frequencies_df.sort_values(by=labels['frequency_col'], ascending=False)
word_frequencies_df = word_frequencies_df.reset_index().rename(columns={'index': labels['words_col']})
word_frequencies_df.to_csv(word_frequencies_path, index=False, encoding="utf-8")


#-----------------------
# WORDS FREQUENCY PLOT
#-----------------------

colors = ['darkgreen'] * 5 + ['lightblue'] * 5
top_words = word_frequencies_df.head(10)
plt.figure(figsize=(12,6))
plt.bar(top_words[labels['words_col']], top_words[labels['frequency_col']], color=colors)
plt.xlabel(labels['xlabel'])
plt.ylabel(labels['ylabel'])
plt.title(labels['top_title'].format())
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig(top_chart_path, dpi=300, bbox_inches="tight")
plt.close()


#-----------------------
# TEXT CLASIFICATION
#-----------------------



print('Successful execution!')