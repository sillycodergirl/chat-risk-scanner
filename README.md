# Chat Risk Sentinel (Scanner)
A Python CLI Program designed to manage a csv of posts, and gives it a risk score.
This was made for a Computer Science project, not made for real uses.

Risk is based off a "risk score", this score is based off the following rules.
- Post contains at least one banned keyword (+1 point)
- Post contains an additional banned keyword (+2 points)
- Post contains a keyword followed by an exclamation mark [e.g "You're an idiot!"] (+2 Points)
- Post contains all uppercase letters [e.g "YOU SUCK"] (+1 Point)

This score is then calcuated using this scale:


| Score | Risk Level |
| :---: | :---: |
| 0 | No Risk |
| 1-2 | Low Risk |
| 3-4 | Medium Risk |
| 5+ | High Risk

## Use of AI
AI was not used during programming, with the single exception of creating a testing csv file.

You are not required to use the given CSV file, and may use a different one using a URL or a local file.

