import streamlit as st

def small_vertical_space(multiplier=1):
    """
    Generate a small vertical space in the Streamlit app by writing newline characters.

    Parameters:
        multiplier (int): The number of newlines to be generated. Default is 1.

    Returns:
        list: Streamlit code
    """
    return [st.write('\n') for _ in range(multiplier)]

def large_vertical_space(multiplier=1):
    """
    Generate a small vertical space in the Streamlit app by writing '#' with streamlit. 

    Parameters:
        multiplier (int): The number of vertical spaces to be generated. Default is 1.

    Returns:
        list: Streamlit code
    """
    return [st.write('#') for _ in range(multiplier)]
