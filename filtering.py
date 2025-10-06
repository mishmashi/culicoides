import streamlit as st
import pandas as pd
import os
import numpy as np
import csv
from io import StringIO
from LLM2vec import get_feature_vector
# Initialize session state
if "index" not in st.session_state:
    database = []
    st.session_state.index = 0
    st.session_state.candidates = database
    st.session_state.eliminated = []
    st.session_state.c_prev = database
    st.session_state.species_initialized = False
    st.session_state.o_prev = []
    st.session_state.u_inp = ""
    st.session_state.clicked_back = False
    st.session_state.answered = []
    st.session_state.just_el = []
    st.session_state.threshold = 0.3

def update_probabilities(ans, index, candidates, thresh, factor=.25):
  just_el = []
  if ans is None:
    return candidates, just_el
  for i, candidate in enumerate(candidates):
    c_ans = candidate.get(index, np.nan)
    if pd.isna(c_ans) or ans == c_ans:
      just_el.append(0)
      if ans == c_ans and not pd.isna(c_ans):  
        candidate["prob"] = candidate["prob"]*1.1
    elif ans != c_ans:
      candidate["prob"] = candidate["prob"]*factor
      if candidate["prob"] < thresh:
        candidate["considered"] = 0
        just_el.append(1) #add index of candidate that was eliminated to list, to be used by filter_candidates
      else:
          just_el.append(0)
      
  max_prob = max(c["prob"] for c in candidates)
  if max_prob >.9:
      for i, candidate in enumerate(candidates):
          candidate["prob"] = candidate["prob"]/max_prob
  return candidates, just_el
      
def filter_candidates(candidates, just_el):
        candidates = [c for c, keep in zip(candidates, just_el) if keep == 0]
        return candidates 
        
 
st.header("Species Identification")
@st.cache_data(ttl=6) #for optimization
def load_data():
        df = pd.read_csv("traits.csv", header=1)
        questions = [col for col in df.columns if col not in ("Species", "Region", "Pathogen", "Considered", "Probability", "Image")]

        database = []
        for _, row in df.iterrows():
            entry = {"name": row["Species"], "prob": row["Probability"], "patho": row["Pathogen"], "considered": row["Considered"], "image": row["Image"], "region": row["Region"]}
            for i, q in enumerate(questions):
                if pd.notna(row[q]) and row[q] != "":
                    entry[i] = int(row[q])
            database.append(entry)

        return questions, database

# ---- Load questions and database ----
questions, database = load_data()
qbs = StringIO(',,,,,,Third palpal segment with sensory organ,Distal spot on the r3 cell distinctly separated from the subapical pale spot; spermathecae unequal sized,No pale spot on the anterior part of vein CuA; smaller spermatheca with non-filiform duct,"Sensory organ on the third palpal segment deep and narrow, opening into a small pore; eyes broadly separated",Third palpal segment elongated; sclerotized ring long and curved; rudimentary spermatheca short,Male specimens: parameres without ventral lobe; distal portion without lateral fringe of spicules')
reader = csv.reader(qbs)
questions_b = [item for item in reader]

# ---- Session Initialization ----
if st.session_state.species_initialized == False:
    st.session_state.index = 0
    st.session_state.candidates = database
    st.session_state.species_initialized = True
    
st.title("Paraensis Group Species Identifier")

st.markdown("Answer the following morphological questions to identify the species of Culicoides:")

# ---- Main Loop ----

_, mid, _ = st.columns(3)
mid.write(f"**Remaining candidates:** {len(st.session_state.candidates)}")
        
if not st.session_state.clicked_back:
    while st.session_state.index < len(questions):
        values = {c.get(st.session_state.index, -1) for c in st.session_state.candidates}
        num_with_values = sum(1 for c in st.session_state.candidates if st.session_state.index in c)
                
        if st.session_state.index >= 10: 
             if num_with_values <= 1:
                 st.session_state.index += 1
             else:
                     break
        else:
             if len(values) <= 1 or num_with_values <= 1:
                 st.session_state.index += 1
             else:
                break
else:
    st.session_state.clicked_back = False
    
if st.session_state.index < len(questions):
    
    q = questions[st.session_state.index]
    q_b = questions_b[0][st.session_state.index+6]
    
    st.write(f"**Q{st.session_state.index}:**")
    col1, col2, col3 = st.columns(3)
    imgstrunique = "images/"+str(st.session_state.index)+".png"
    if os.path.exists(imgstrunique):
        st.image(imgstrunique, use_container_width=True)
    else:
        tr, fal = st.columns(2)
        imgstry = "images/"+str(st.session_state.index)+"a.png"
        imgstrn = "images/"+str(st.session_state.index)+"b.png"
        if os.path.exists(imgstry):
            tr.image(imgstry, use_container_width=True)
        if os.path.exists(imgstrn):
            fal.image(imgstrn, use_container_width=True)
    if col1.button(q,key=f"q_sp_{st.session_state.index}", use_container_width = True):
        st.session_state.c_prev = st.session_state.candidates            
        candidates, st.session_state.just_el = update_probabilities(1, st.session_state.index, st.session_state.candidates, st.session_state.threshold)
        st.session_state.candidates = filter_candidates(st.session_state.candidates, st.session_state.just_el)
        removed = [e for e in st.session_state.c_prev if e not in st.session_state.candidates]
        st.session_state.eliminated.append(removed)
        st.session_state.answered.append(st.session_state.index)
        st.session_state.index += 1
        st.rerun()
      
    if col3.button(f"{q_b}",key=f"qb_sp_{st.session_state.index}", use_container_width = True):
        st.session_state.c_prev = st.session_state.candidates      
        candidates, st.session_state.just_el = update_probabilities(0, st.session_state.index, st.session_state.candidates, st.session_state.threshold)
        st.session_state.candidates = filter_candidates(st.session_state.candidates, st.session_state.just_el)
        removed = [e for e in st.session_state.c_prev if e not in st.session_state.candidates]
        st.session_state.eliminated.append(removed)
        st.session_state.answered.append(st.session_state.index)
        st.session_state.index += 1
        st.rerun()
      
    if col2.button("I don't know",key=f"idk_hasqb_sp_{st.session_state.index}", use_container_width = True):
        st.session_state.c_prev = st.session_state.candidates
        removed = [[]]
        st.session_state.eliminated.append(removed)
        st.session_state.answered.append(st.session_state.index)
        st.session_state.index += 1
        st.rerun()

else:
    if len(st.session_state.candidates) == 1:
        st.success(f"The specimen is a **Culicoides (Haematomyidium) {st.session_state.candidates[0]['name']}**")
        imgstr = "images/"+str(st.session_state.candidates[0]['name'])+".png"
        if os.path.exists(imgstr):
            st.image(imgstr, use_container_width=True)
    elif len(st.session_state.candidates) > 1:
        st.session_state.candidates = sorted(st.session_state.candidates, key=lambda c: c['prob'], reverse=1)
        probs = sorted(list(set([candidate.get('prob') for candidate in st.session_state.candidates if candidate.get('prob') is not None])), reverse=True)
        st.markdown("Most likely species: ")

        if st.session_state.candidates and st.session_state.candidates[0].get('prob') is not None:
            highest_prob = st.session_state.candidates[0]['prob']
            n_printed = 0
            for candidate in st.session_state.candidates:
                if candidate.get('prob') == highest_prob:
                    st.success(f"**Culicoides (Haematomyidium) {candidate['name']}** (Confidence: {candidate['prob']*100}%)")
                    imgstr = "images/"+str(candidate['name'])+".png"
                    if os.path.exists(imgstr):
                        st.image(imgstr, use_container_width=True)
                    n_printed +=1
                else:
                    break
        
        if len(probs) > 1:
          threshold_prob = probs[0] - .2
          if probs[1] >= threshold_prob:
            
            # Start from the first candidate whose probability is less than the highest_prob
            start_index_other = n_printed
            if st.session_state.candidates and st.session_state.candidates[0].get('prob') is not None:
                 highest_prob = st.session_state.candidates[0]['prob']
                 for candidate in st.session_state.candidates:
                     if candidate.get('prob') < highest_prob or candidate.get('prob') is None:
                         start_index_other += 1
                         break
            
            for candidate in st.session_state.candidates[start_index_other:]: 
                if candidate.get('prob') is not None and candidate['prob'] >= threshold_prob:
                     st.write(f"- **Culicoides (Haematomyidium) {candidate['name']}** (Confidence: {candidate['prob']*100:.1f}%)")
                     imgstr = "images/"+str(candidate['name'])+".png"
                     if os.path.exists(imgstr):
                       st.image(imgstr, use_container_width=True)
                else:
                    break
        elif len(st.session_state.candidates) > 1:
            for candidate in st.session_state.candidates[start_index_other:]:
                 st.write(f"- **Culicoides (Haematomyidium) {candidate['name']}** (Confidence: {candidate['prob']*100:.1f}%)")
    else:
      st.error("No matching relevant species.")

bn1, bn2 = st.columns(2)
    
if st.session_state.index > 0:
    if bn1.button("Previous question",key="prev_spec", use_container_width=True)  and st.session_state.answered:
        st.session_state.index = st.session_state.answered.pop()
        restore = st.session_state.eliminated.pop()
        st.session_state.candidates.extend(e for e in restore if isinstance(e, dict))
        st.session_state.clicked_back = True
        st.rerun()
        

if bn2.button("Restart",key="restart_sp", use_container_width = True):
    st.session_state.index = 0
    st.session_state.eliminated = []
    st.session_state.candidates = database
    st.session_state.species_initialized = False
    st.rerun()
st.markdown("Coetzee, M. Key to the females of Afrotropical Anopheles mosquitoes (Diptera: Culicidae). Malar J 19, 70 (2020). https://doi.org/10.1186/s12936-020-3144-9")
#if len(st.session_state.others) >0:
#  if st.button("See rare species"):
#    for name in others:
#          st.write("- " + name)
