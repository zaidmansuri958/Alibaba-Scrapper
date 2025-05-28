import pandas as pd

def clean_and_save_data(df):
    # Drop unnecessary columns
    df.drop(columns=['product_url', 'image_url'], inplace=True)

    # Remove "$" and "," from price
    df["cleaned_price"] = df["price"].str.replace(r"[\$,]", "", regex=True)

    # Split price into min and max
    price_split = df["cleaned_price"].str.split("-", expand=True)

    # Convert to float (use errors='coerce' to avoid conversion issues)
    df["min_price"] = pd.to_numeric(price_split[0], errors='coerce')
    df["max_price"] = pd.to_numeric(price_split[1], errors='coerce')

    # Fill missing max_price with min_price
    df["max_price"] = df["max_price"].fillna(df["min_price"])

    # Clean rating text
    df["rating_text_cleaned"] = df["rating_text"].str.replace("\n/5.0", "", regex=False)

    # Extract numeric rating and number of ratings
    df['rating'] = df['rating_text_cleaned'].str.extract(r'(\d+\.?\d*)')
    df['num_ratings'] = df['rating_text_cleaned'].str.extract(r'\(\s*(\d+)\s*\)').astype(float)

    # Extract minimum order quantity
    df["min_order"] = df["min_order"].str.extract(r'(\d+)').astype(float)

    # Drop intermediate columns
    df.drop(columns=['rating_text', 'rating_text_cleaned', 'cleaned_price', 'price'], inplace=True)

    # Save cleaned data
    df.to_csv("./cleaned_data.csv", index=False)
    print("✅ Cleaned data saved to ./cleaned_data.csv")

if __name__ == "__main__":
    df = pd.read_excel("E:/WebScraping/Alibaba-scraping/electronic_data.xlsx")
    clean_and_save_data(df)
