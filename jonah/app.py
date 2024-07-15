import streamlit as st
from jonah import clean, compare
import os

# Streamlit interface
st.title('JonAhPP')

# File uploader widgets
file1 = st.file_uploader("Choose the first Excel file", type=['xlsx'])
file2 = st.file_uploader("Choose the second Excel file", type=['xlsx'])

# Run button
if st.button('Run'):
    if file1 is not None and file2 is not None:
        result, log = compare(clean(file1), clean(file2))
        result.to_csv('diff.csv', index=False)
        log.append(f'Output saved to {os.path.abspath("diff.csv")}')
        st.text_area('Result:', value='\n'.join(log), height=300)
    else:
        st.error('Please upload both files before running.')


def run_streamlit_app():
    import subprocess
    from importlib import resources

    with resources.path('jonah', 'app.py') as app_path:
        subprocess.run(["streamlit", "run", str(app_path)])
