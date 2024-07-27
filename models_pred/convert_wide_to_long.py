import pandas as pd

# Load the dataset into a pandas DataFrame
df = pd.read_excel('D:/StudySpace/Nam3_KyHe/DSinPython/crawler/new_selenium_env/phone_data_ver0.xlsx')

# Create an empty list to store the long data
long_data = []

# Iterate through the DataFrame
for index, row in df.iterrows():
    product_name = row['product_name'] # tuple indices must be integers or slices, not str so the "index" must be needed in the for loop
    
    # Iterate through the comment and rating columns
    for i in range(1, 581):  # 580 is the number of comments (comment + rating) columns in the dataset
        comment_col = f'comment_{i}'
        rating_col = f'rating_{i}'
        comment = row[comment_col]
        rating = row[rating_col]
        
        # Add to the long_data list if there's data (Data cleaning - delete missing values)
        if pd.notna(comment) and pd.notna(rating):
            long_data.append([product_name, comment, rating])

# Create a new DataFrame from the long_data list
df_long = pd.DataFrame(long_data, columns=['product_name', 'comment', 'rating'])

# Save the long format DataFrame to an Excel file
df_long.to_excel('phone_data_long.xlsx', index=False)