import streamlit as st

st.title("Species Identification App")
st.write("Upload an image or enter a species name to get information!")

# For now, just basic input placeholders
image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
species_name = st.text_input("Or enter species name")

if st.button("Search"):
    st.write("This is where the search logic will go.")
