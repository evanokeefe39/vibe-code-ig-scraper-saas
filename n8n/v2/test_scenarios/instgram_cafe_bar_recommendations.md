# Example Scenario / Use Case

I am a user who wants to get the last 30 days of posts across these creators profiles. I want to extract recommendations for bars, cafes, resturaunts etc. for young people 18 - 35 you are studying, working or travelling to the area. maximum 10 posts total as im just testing this app.

## Sources

### Instagram Profiles:

https://www.instagram.com/parisfoodguide_/
https://www.instagram.com/ellevousguide/
https://www.instagram.com/_lavieparisienne__/

### Constraints
Last 30 days, Max 10 posts in total

## Extraction Prompt

From the post caption i want:
- the name of the place that is recommended, i.e could be the name of a cafe, a point of interest like a garden/park.
- the address
- labels for the vibe of the place e.g cool, chic, hip, artsy, romantic, exciting, natural_beauty, cosy, good_value, trendy, elegant, modern, creative, lively, scenic, warm, intimate, affordable, energetic, neutral etc.
- extract any notes made about the cost
- confidence score for extraction

## Extraction Prompt 2

From the post caption i want:
- the name of the place that is recommended, i.e could be the name of a cafe, a point of interest like a garden/park.
- the address
- the profile name of the place if it's mentioned e.g @nobofrance, @ritzparis
- labels for the vibe of the place e.g cool, chic, hip, artsy, romantic, exciting, natural_beauty, cosy, good_value, trendy, elegant, modern, creative, lively, scenic, warm, intimate, affordable, energetic, neutral etc.
- extract any notes made about the cost
- confidence score for extraction

If multiple recommendations in one post make sure to get all of them!






