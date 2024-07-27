import pandas as pd
from transformers import pipeline
import time

# Load the pre-trained correction model
corrector = pipeline("text2text-generation", model="bmd1905/vietnamese-correction")

# Load DataFrame
df_long = pd.read_excel('phone_data_long.xlsx')

# Apply the correction model to the "comment" column and show progress
MAX_LENGTH = 512 
total_comments = len(df_long)
start_time = time.time()

for i, row in df_long.iterrows():
    df_long.loc[i, 'corrected_comment'] = corrector(row['comment'], max_length=MAX_LENGTH)[0]['generated_text']

    # Print progress
    if (i + 1) % 10 == 0:  # Print every 10 comments
        elapsed_time = time.time() - start_time
        print(f"Corrected {i + 1}/{total_comments} comments ({elapsed_time:.2f} seconds)")

# Save the updated DataFrame
df_long.to_excel('phone_data_long_corrected.xlsx', index=False)