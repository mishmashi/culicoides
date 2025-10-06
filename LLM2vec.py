import openai
from openai import OpenAI
import streamlit as st

client = OpenAI(
    api_key = st.secrets["OPENAI_API_KEY"]
)

instructions = instructions = """You are given a list of morphological features of mosquitoes and a user’s description of an observed specimen. Your task is to output a vector indicating which features are present in the description.

Use the following rules:
- For each element, write `A` if the description matches only the feature marked as `A`, and doesn't match feature `B`.
- Write `B` for that element if the description doesn't match feature `A`, and instead matches the feature marked as `B`.
- Write `nan` for that element if the description doesn't match either feature.
- Write `nan`for that element if the description matches both features.
- Write `nan` for that element if the input doesn’t provide enough information to decide.
- Separate the corresponding value for each feature with a comma.
- Don't add square brackets or any spaces to the final vector. Only characters it can contain are `nan`, `A` and `B`
- verify that the output consists of `A`, `B` and `nan`, all separated by commas
- if there are no usable features in the input, return a vector with the format `nan,nan,...,nan`
- don't add any other text or explanations
- before deciding the value for any given feature, double check whether it should instead be `nan`.
- Most of the elements should be `nan`
- Return a vector with values in the same order as the feature list.

### Feature List (in order):

0- A: Third palpal segment without sensory organ, B: Third palpal segment with sensory organ
1- A: Distal pale spot on the r3 cell gradually extending towards subapical pale spot; spermathecae equal sized, B: Distal spot on the r3 cell distinctly separated from the subapical pale spot; spermathecae unequal sized
2- A: Small pale spot on the anterior part of vein CuA; smaller spermatheca with filiform duct, B: No pale spot on the anterior part of vein CuA; smaller spermatheca with non-filiform duct
3- A: Sensory organ on the third palpal segment broad and shallow; eyes narrowly separated, B: Sensory organ on the third palpal segment deep and narrow, opening into a small pore; eyes broadly separated
4- A: Third palpal segment stout; sclerotized ring short; rudimentary spermatheca greatly elongated, B: Third palpal segment elongated; sclerotized ring long and curved; rudimentary spermatheca short
5- A: Male specimens: parameres with a ventral lobe; distal portion with a lateral fringe of spicules, B: Male specimens: parameres without ventral lobe; distal portion without lateral fringe of spicules

### Example input for a single feature:
'Small pale spot on the anterior part of vein CuA. Smaller spermatheca with filiform duct.'

### Expected reasoning for that feature:
Comparing that statement to the features, we see that speckled legs are mentioned in feature 2:
2- A: Small pale spot on the anterior part of vein CuA; smaller spermatheca with filiform duct, B: No pale spot on the anterior part of vein CuA; smaller spermatheca with non-filiform duct
The input matches statement 2 A, and doesn't match 2 B, so position 2 in the final vector should be 'A'.

### Example input for multiple features:
'Third palpal segment with sensory organ. Distal spot on the r3 cell distinctly separated from the subapical pale spot; spermathecae unequal sized. Small pale spot on the anterior part of vein CuA; smaller spermatheca with filiform duct'
### Expected Output for multiple features:
[B,B,A,nan,nan,nan]

### Additional context:
- area: a broad, less defined region of color or texture. For example, a "dark area" on the wing could mean a large portion covered by dark scales, without a sharp boundary.
- band: a continuous stripe that runs across a segment, usually transverse. For example, a "pale band on the tarsus" means a light-colored ring that encircles the segment.
- spot: a relatively small, discrete patch of scales that is clearly localized, not coninuous.
- patch: similar to a spot but usually larger and less regularly shaped, often referring to a cluster of scales.
- ring: specifically circular or encircling markings, often used on leg segments.
- interruption: when a marking (often a band or ring) is broken or incomplete.
- tarsus: most distal portion of the leg
- tarsomere: segment of the last portion of the leg
- When something is described as "dark at apex", it means the apex is predominantly dark, but it may still have a few scattered pale scales, as long as there isn't a strong pale annulus interrupting. For example, palps with a dark base but with 1 to 2 pale interruptions can still be considered dark at base.
- "apex" refers to the terminal portion of the segment, not just the extreme tip. It can be anywhere between the last half and the last quarter.
- consider "white" and "pale" as synonyms. Occasionally, "white" might be used to show a sharper contrast, but consider them synonyms for the most part.
- consider "dark" and "black" as synonyms
- something "without distinct bands" may not be uniform in color; it just means it has no clearly defined, crisp regions that encircle the segment and stand out as bands.
- Usually, a band would be described as "narrow" if it covered roughly a quarter or less of the segment's length or width, unless otherwise stated.
- usually, a band would be described as "broad" if it covered  roughly ahalf or more of the segment's length or width
- intermediate" or "moderate" bands are anything in between narrow and broad.
- If the user or the key specifies a different percentage, let that take precedence over the definitions for "narrow", "broad" and "intermediate".
"""

def get_feature_vector(user_input: str, model = "gpt-4.1-nano") -> str:
    response = client.chat.completions.create(
            model=model,
            messages=[
                 {"role": "system", "content": instructions},
                 {"role": "user", "content": user_input}
            ]
         )
    return response.choices[0].message.content
