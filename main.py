import streamlit as st
import pandas as pd

# Load data from Excel
@st.cache_data
def load_name_list_from_excel(file_path, sheet_name, column_name):
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        name_list = df[column_name].dropna().tolist()
        return name_list
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return []

# Function to search part number based on user input
def search_part_number(query, name_list):
    query = query.strip().lower()
    if '/' in query:
        substrings = query.split('/')
        matches = [
            entry for entry in name_list 
            if any(substring in entry.lower() for substring in substrings)
        ]
    else:
        substrings = query.split()
        matches = [
            entry for entry in name_list 
            if all(substring in entry.lower() for substring in substrings)
        ]
    return matches

# Function to highlight search terms in results
def highlight_matches(text, substrings, color="yellow"):
    for substring in substrings:
        if substring:
            text = text.replace(
                substring, 
                f"<mark style='background-color:{color};'>{substring}</mark>"
            )
    return text

# Main Streamlit app function
def main():
    st.set_page_config(page_title="Part Number Search", layout="wide")
    
    st.title("Part Number Search App")
    st.markdown("Search for part numbers by entering the description below.")
    
    # Load Excel data
    name_list = load_name_list_from_excel(
        'data/part_number_app_data.xlsx', 
        'Sheet1', 
        'NAME LIST'
    )
    
    # User input for searching part numbers
    query = st.text_input("Enter Part Number Description", placeholder="e.g., ABC/123")
    
    # Search button
    if st.button("Search"):
        if not query:
            st.warning("Please enter a search query.")
        else:
            # Split query into substrings for highlighting
            substrings = query.lower().split('/')
            matches = search_part_number(query, name_list)
            
            # Display results
            if matches:
                st.success(f"Found {len(matches)} match(es).")
                for match in matches:
                    # Highlight substrings in results
                    highlighted_text = highlight_matches(match.lower(), substrings, color="lightgreen")
                    st.markdown(f"<div style='font-size: 18px;'>{highlighted_text}</div>", unsafe_allow_html=True)
            else:
                st.error("No matches found.")

if __name__ == '__main__':
    main()
