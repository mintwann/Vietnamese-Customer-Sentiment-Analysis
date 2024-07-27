import pandas as pd
from sentence_transformers import SentenceTransformer
from pyvi.ViTokenizer import tokenize

# Load dataset
df = pd.read_excel("D:/StudySpace/Nam3_KyHe/DSinPython/dataset/phone_data_for_sen2vec.xlsx")

# Load the Vietnamese embedding model
model = SentenceTransformer('dangvantuan/vietnamese-embedding')

# for counting the number of processed comments
total_comments = len(df)
processed_count = 0
max_length = 512  # max sequence length for the model
def get_embedding(text):
    global processed_count
    processed_count += 1
    if processed_count % 10 == 0 or processed_count == total_comments:
        print(f"Processed {processed_count}/{total_comments} comments")
        
    try:
        tokenized_text = tokenize(text)
        tokenized_text = tokenized_text[:max_length]
        embedding = model.encode(tokenized_text)
    except Exception as e:
        print(f"Error processing comment: {text}")
        print(e)
        embedding = [0] * model.get_sentence_embedding_dimension() # return a vector of zeros if an error occurs
    return embedding

# Apply the modified function
df['vector'] = df['corrected_comment'].apply(get_embedding)

# Split the vector into columns
vector_df = pd.DataFrame(df['vector'].values.tolist(), columns=[f'dim_{i}' for i in range(model.get_sentence_embedding_dimension())])
df = pd.concat([df, vector_df], axis=1)
df = df.drop('vector', axis=1)

# Reorder columns
new_column_order = ['corrected_comment'] + [f'dim_{i}' for i in range(model.get_sentence_embedding_dimension())] + ['sentiment']
df = df[new_column_order]

# Save the updated DataFrame to a new Excel file
df.to_excel("phone_data_with_vectors.xlsx", index=False) 