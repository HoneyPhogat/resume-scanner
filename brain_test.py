import re
import nltk
from nltk.stem import PorterStemmer

# The raw, messy data
resume_text = "Honey Phogat is a Python Developer. • Knows SQL, FastAPI, and Java."
jd_text = "Looking for a python developer who knows fastapi."

# --------------------------------------
#      CLEANING THE RESUME
# --------------------------------------
print("--- ORIGINAL RESUME ---")
print(resume_text)

# Making everthing lowercase
resume_lower = resume_text.lower()
print("\n --- LOWERCASE RESUME ---")
print(resume_lower)

# To remove the special characters and punctuations
resume_scrubbed = re.sub(r'[^a-z0-9\s]', ' ', resume_lower)
print("\n --- SCRUBBED RESUME ---")
print(resume_scrubbed)

# To make it into a list of works
resume_words = resume_scrubbed.split()
print("\n -- RESUME WORDS --")
print(resume_words)

# --------------------------------------
#    CLEANING THE JOB DESCRIPTION 
# --------------------------------------

jd_lower = jd_text.lower()
jd_scrubbed = re.sub(r'[^a-z0-9\s]', ' ', jd_lower)
jd_words = jd_scrubbed.split()
print("\n -- JOB DESCRIPTION WORDS --")
print(jd_words)

# --------------------------------------
#   CHECKHING THE SCORE AND MATCH
# --------------------------------------

# Removing the duplicates 
resume_set = set(resume_words)
jd_set = set(jd_words)


# To match the words
matched_words = resume_set.intersection(jd_set)
print("\n--- MATCH RESULTS ---")
print(f"Total Words in JD: {len(jd_set)}")
print(f"Matches Found: {len(matched_words)}")
print(f"The Exact Matches: {matched_words}")

# Calculating the score
score = len(matched_words) / len(jd_set) * 100
print(f"Match Score: {score:.2f}%")