import streamlit as st
import pandas as pd
from typing import List, Set
import re
from functools import lru_cache
from collections import defaultdict

# Create an inverted index for faster searching
class SearchIndex:
    def __init__(self):
        self.index = defaultdict(set)
        self.entries = []
        
    def add_entry(self, entry: str, idx: int):
        # Convert to lowercase for case-insensitive search
        words = set(re.findall(r'\w+', entry.lower()))
        for word in words:
            self.index[word].add(idx)
        self.entries.append(entry)
    
    def build_from_list(self, entries: List[str]):
        self.index.clear()
        self.entries.clear()
        for idx, entry in enumerate(entries):
            self.add_entry(entry, idx)
    
    def search(self, query: str) -> List[str]:
        if not query:
            return []
        
        # Split query into words and handle both space and slash separators
        query_words = set(re.findall(r'\w+', query.lower()))
        
        if not query_words:
            return []
        
        # Get the first word's matching indices
        if query_words:
            first_word = next(iter(query_words))
            result_indices = self.index.get(first_word, set())
        else:
            return []
            
        # Intersect with other words' indices
        for word in query_words:
            result_indices &= self.index.get(word, set())
            
        return [self.entries[idx] for idx in result_indices]

# Cache the data loading
@st.cache_data
def load_name_list_from_excel(file_path: str, sheet_name: str, column_name: str) -> tuple:
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        name_list = df[column_name].dropna().tolist()
        # Create and build search index
        search_index = SearchIndex()
        search_index.build_from_list(name_list)
        return name_list, search_index
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return [], None

@st.cache_data
def highlight_matches(text: str, substrings: List[str], color: str = "yellow") -> str:
    """Cache the highlighting function for better performance"""
    text_lower = text.lower()
    for substring in substrings:
        if not substring:
            continue
        pattern = re.compile(f'({re.escape(substring)})', re.IGNORECASE)
        text = pattern.sub(f'<mark style="background-color:{color};">\\1</mark>', text)
    return text

def main():
    st.set_page_config(page_title="Part Number Search", layout="wide")
    
    st.title("Part Number Search App")
    st.markdown("Search for part numbers by entering the description below.")
    
    # Load Excel data and create search index
    name_list, search_index = load_name_list_from_excel(
        'part_number_app_data.xlsx',
        'Sheet1',
        'NAME LIST'
    )
    
    if search_index is None:
        st.error("Failed to initialize search index.")
        return
    
    # User input for searching part numbers
    query = st.text_input("Enter Part Number Description", placeholder="e.g., ABC/123")
    
    # Search button
    if st.button("Search") or query:  # Also trigger search on query input
        if not query:
            st.warning("Please enter a search query.")
        else:
            # Get search results using the inverted index
            matches = search_index.search(query)
            
            # Display results
            if matches:
                st.success(f"Found {len(matches)} match(es).")
                
                # Extract words for highlighting
                highlight_terms = re.findall(r'\w+', query.lower())
                
                # Create columns for better layout
                cols = st.columns([3, 1])
                with cols[0]:
                    for match in matches:
                        highlighted_text = highlight_matches(
                            match,
                            highlight_terms,
                            color="lightgreen"
                        )
                        st.markdown(
                            f"""<div style='font-size: 18px; padding: 5px; 
                            border-bottom: 1px solid #eee;'>{highlighted_text}</div>""",
                            unsafe_allow_html=True
                        )
            else:
                st.error("No matches found.")

if __name__ == '__main__':
    main()
