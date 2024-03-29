# Import 3rd party libraries
import streamlit as st
import streamlit.components.v1 as components

# Import from standard library
import logging
import random
import re
import pdfplumber # PyPDF2
from io import StringIO

# Import openai module 
import openai_wrapper

# Configure logger
logging.basicConfig(format="\n%(asctime)s\n%(message)s", level=logging.INFO, force=True)

st.set_page_config(page_title="Cover letter", page_icon="🤖", layout="wide")

max_resume_page = 2

max_context_size = 4096

def read_resume(file):
    resume = ""
    with pdfplumber.open(file) as pdf:
        pages = pdf.pages
        if (len(pages) > max_resume_page):
          st.session_state.text_error = "Resume too long." + " Max supported page: " + str(max_resume_page)
          logging.info(f"File name: {file} too big\n")
          st.error(st.session_state.text_error)
          return ""
        for p in pages:
            resume = resume + p.extract_text()
    logging.info("Number of words in resume: " + str(len(resume.split())))
    return resume

def resume_upload_callback():
  if st.session_state['resume_uploader'] is not None:
    st.session_state["resume_ctr"] += 1
    st.session_state["resume_text"] = read_resume(st.session_state['resume_uploader'])

def prompt_tunning(resume_text: str, job_description: str, letter_size: int):
  prompt = "Write a cover letter with following resume and job description: "
  prompt = prompt + resume_text + job_description
  num_prompt_words = len(prompt.split())
  if (num_prompt_words + letter_size > max_context_size):
    err_str = f"Prompt + letter size are too big to handle: {num_prompt_words} and {letter_size}"
    st.session_state.text_error = err_str
    logging.info(err_str)
    st.error(err_str)
    return None

  logging.info("Number of words in prompt: " + str(num_prompt_words))
  return prompt

def generate_receipes(resume_text: str, job_description: str):
  if st.session_state.n_requests >= 5:
    st.session_state.text_error = "Too many requests. Please wait a few seconds before generating another letter."
    logging.info(f"Session request limit reached: {st.session_state.n_requests}")
    st.session_state.n_requests = 1
    return

  if not resume_text:
    err_str = "Resume is empty"
    logging.info(err_str)
    st.error(err_str)
    return

  if not job_description:
    err_str = "Job description is empty"
    logging.info(err_str)
    st.error(err_str)
    return

  #with text_spinner_placeholder:
  with st.spinner("Please wait while your letter is being generated..."):
    prompt = prompt_tunning(resume_text, job_description, st.session_state.letter_size)
    if not prompt:
      logging.info (f"Couldn't configure prompt successfully")
      return

    openai = openai_wrapper.Openai()
    flagged = openai.moderate(prompt)
    # cleanup previous errors
    if flagged:
      st.session_state.text_error = "Input flagged as inappropriate."
      return
    else:
      st.session_state.text_error = ""
      st.session_state.n_requests += 1

      response = openai.complete(prompt, 0, st.session_state.letter_size)
      st.session_state.cover_letter = response[0]
      st.session_state.total_tokens_used = st.session_state.total_tokens_used + response[1] 

      logging.info (f"Successfully generated cover letter")

  return

def ingredients_callback():
  return

def list_assumed_ingredients():
  col0, col1, col2, col3, col4, col5, col6, col7, col8, col9= st.columns(10)

  st.session_state.ingredients["Potatoes"] = col0.checkbox("Potatoes", value=True)

  st.session_state.ingredients["Tomatoes"] = col1.checkbox("Tomatoes", value=True) 

  st.session_state.ingredients["Onions"] = col2.checkbox("Onions", value=True) 

  st.session_state.ingredients["Cauliflower"] = col3.checkbox("Cauliflower", value=True) 

  st.session_state.ingredients["Peas"] = col4.checkbox("Peas", value=True) 

  st.session_state.ingredients["Carrots"] = col5.checkbox("Carrots", value=True) 

  st.session_state.ingredients["Bell peppers"] = col6.checkbox("Bell peppers", value=True) 

  st.session_state.ingredients["Eggplant"] = col7.checkbox("Eggplant", value=True) 

  st.session_state.ingredients["Spinach"] = col8.checkbox("Spinach", value=True) 

  st.session_state.ingredients["Okra"] = col9.checkbox("Okra", value=True) 

  col10, col11, col12, col13, col14, col15, col16, col17, col18, col19= st.columns(10)

  st.session_state.ingredients["Cinnamon"] = col0.checkbox("Cinnamon", value=True)

  st.session_state.ingredients["Cumin"] = col1.checkbox("Cumin", value=True) 

  st.session_state.ingredients["Coriander"] = col2.checkbox("Coriander", value=True) 

  st.session_state.ingredients["Garlic"] = col3.checkbox("Garlic", value=True) 

  st.session_state.ingredients["Ginger"] = col4.checkbox("Ginger", value=True) 

  st.session_state.ingredients["Turmeric"] = col5.checkbox("Turmeric", value=True) 

  st.session_state.ingredients["Red chilli"] = col6.checkbox("Red chilli", value=True) 

  st.session_state.ingredients["Mustard"] = col7.checkbox("Mustard", value=True) 

  st.session_state.ingredients["Cardamom"] = col8.checkbox("Cardamom", value=True) 

  st.session_state.ingredients["Cloves"] = col9.checkbox("Cloves", value=True) 


  ## TODO: delete later
  st.write( st.session_state.ingredients)


# Setup session state
if "receipe_type" not in st.session_state:
  st.session_state.receipe_type = ""

if "ingredients" not in st.session_state:
  # use dictionary to include to remove specific items. 
  st.session_state.ingredients = {}

if "cover_letter" not in st.session_state:
  st.session_state.cover_letter = ""

if "letter_size" not in st.session_state:
  st.session_state.letter_size = 200 # small

if "resume_ctr" not in st.session_state:
  st.session_state.resume_ctr = 0

if "n_requests" not in st.session_state:
  st.session_state.n_requests = 0

if "total_tokens_used" not in st.session_state:
  st.session_state.total_tokens_used = 0

if "text_error" not in st.session_state:
  st.session_state.text_error = ""

# Render main page
with st.container():

  title = "Personalized Recipes!!"
  st.title(title)
  st.markdown("No account signup, Just provide ingredients and get receipe recommendations.")
  #st.markdown("Generated via OpenAI's ChatGPT [Davinci model](https://beta.openai.com/docs/models/overview).")
  #st.markdown("Author's [LinkedIn](https://www.linkedin.com/in/manoj-tiwari-17b9213/). Feel free to connect!")

  st.text_input(label="Add/Remove Ingredients", placeholder="add/remove/paste ingredients",
    on_change=ingredients_callback,
    key="ingredients_input")

  list_assumed_ingredients()  
    
  st.markdown("Reciepes based on above ingredients list.")

  st.button(
      label="Generate receipes",
      type="primary",
      on_click=generate_receipes,
      args=(st.session_state["receipe_type"], st.session_state["ingredients"]),
      )

  #text_spinner_placeholder = st.empty()
  if st.session_state.text_error:
      st.error(st.session_state.text_error)

  # if st.session_state.cover_letter:
  st.markdown("""---""")
  total_cost = str((st.session_state.total_tokens_used / 1000) * 0.02)
  # make it red & bold
  total_cost = f"**:red[${total_cost}]**"
  st.markdown("Total cost incurred: " + total_cost +
    " (Please support the service if you like your cover letter!!)")

  st.text_area(label="Cover Letter", value=st.session_state.cover_letter, height=500)

contact_form = """
<form action="https://formsubmit.co/manoj41@gmail.com" method="POST">
     <input type="hidden" name="_captcha" value="false">
     <input type="text" name="name" placeholder="Your name" required>
     <input type="email" name="email" placeholder="Your email"" required>
     <textarea name="message" placeholder="Your message here"></textarea>
     <button type="submit">Send</button>
</form>
"""
st.header(":mailbox: Get in touch with me!")
st.markdown(contact_form, unsafe_allow_html=True) 

# Use local css file
def local_css(file_name):
  with open(file_name) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


local_css("style/style.css")
