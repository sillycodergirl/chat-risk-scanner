#!/usr/bin/env python3
'''
    MIT License

    Copyright (c) 2026 SillyCoderGirl

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.

    #####################################
    
    A Python CLI Program designed to manage a csv of posts, and gives it a risk score. 
    This was made for a Computer Science project, not made for real uses.

    PLEASEEEE i rushed coding this, this is nothing serious, let it be a mess. pleaseeeeeeee
'''

import re
import io
import json
import os
import requests
import pandas as pd
from enum import Enum
from time import sleep
from pathlib import Path

# dude this is so fucking cool lmao
class ANSIColor(Enum):
    GREEN = "\033[97;42m"
    YELLOW = "\033[30;103m"
    RED = "\033[1;37;41m"
    RESET = "\033[0m"

    @staticmethod
    def format_color(content, color):
      '''
        Formats the given content with the given ANSI color code. 
        If the color is None or an empty string, it returns the content as a string without any formatting.
        It will automatically reset the color after the content to avoid affecting subsequent text.
      '''
      if color is None or color == "":
        return str(content)

      return f"{color.value}{content}{ANSIColor.RESET.value}"

exitProgram = False

def load_frame():
    '''
        Loads post data from a given source (which is an URL or a local file path) and stores it to loaded_data.
        Must be a CSV file.
    '''
    global loaded_data
    source = input("Enter the source (URL or local file path) for the CSV file: ")

    if re.match(r'^https?://', source):
        response = requests.get(source)
        response.raise_for_status()
        data = response.content.decode('utf-8-sig')
        loaded_data = pd.read_csv(io.StringIO(data), sep=',', engine='python', quotechar='"')
    else:
        try:
          loaded_data = pd.read_csv(source, engine='python')
        except FileNotFoundError:
          print(f"File not found! ({source}) Returning in 2 seconds.\n")
          sleep(2)
          handle_menu()
        except:
          print("Error! Returning in 2 seconds.\n")
          handle_menu()

        if loaded_data is None or loaded_data.empty:
          return
    loaded_data = loaded_data.reset_index(drop=True)
    print()
    handle_menu()

def manage_keywords():
    '''
        Displays a menu for managing keywords. Allows the user to view, add, or remove keywords.
    '''
    print("=== MANAGE KEYWORDS ===")
    print("1. View Keywords")
    print("2. Add Keyword")
    print("3. Remove Keyword")
    print("4. Return to main menu")

    choice = input("Select an option (1-4): ")
    word_list = get_keywords()

     #i would make a better menu engine for this but i dont wanna so take this hack instead
    if choice == "1":
        print("Current Keywords:")
        for keyword in word_list:
            print(f"- {keyword.lower()}")
        print()

    elif choice == "2":
        new_keyword = input("Enter a new keyword to add: ").lower()
        if new_keyword not in word_list:
            word_list.append(new_keyword)
            with open('word_list.json', 'w') as f:
                json.dump(word_list, f)
            print(f"Keyword '{new_keyword}' added.\n")
        else:
            print(f"Keyword '{new_keyword}' already exists.\n")

    elif choice == "3":
        keyword_to_remove = input("Enter a keyword to remove: ").lower()
        if keyword_to_remove in word_list:
            word_list.remove(keyword_to_remove)
            with open('word_list.json', 'w') as f:
                json.dump(word_list, f)
            print(f"Keyword '{keyword_to_remove}' removed.\n")
        else:
            print(f"Keyword '{keyword_to_remove}' not found. \n")
    elif choice == "4":
      handle_menu()
      return # avoid looping

    manage_keywords()  # loop

def get_keywords():
  '''
  Loads the keywords from the word_list.json file and returns them as a list.
  '''
  with open('word_list.json', 'r') as f:
        word_list = json.load(f)
  return word_list


# Risk scoring:
# Keyword +1 per keyword
# Any keyword with an "!" at the end +2
# Contains 2 or more keywords +2
# All caps +1
def analyze_data():
  '''
  Analyzes the loaded data for posts that match the keywords and calculates a risk score for each post.
  '''
  global loaded_data
  global filtered_posts
  global matches

  filtered_posts = []
  matches = {}

  if loaded_data is None or loaded_data.empty:
    print("No data is currently loaded! Would you like to load data?")
    choice = input("Y/n").strip().lower()
    if choice == 'y':
      load_frame()
    else:
      handle_menu()
    return

  keywords = [word.strip().lower() for word in get_keywords() if word.strip()]


  for post_id, row in loaded_data.iterrows():
    post = str(row['post'])
    score = 0
    found_keywords = []

    for keyword in keywords:
      pattern = rf'\b{re.escape(keyword)}\b'
      regMatch = re.search(pattern, post, re.IGNORECASE)

      if regMatch:
        found_keywords.append(keyword)
        score += 1

        if re.search(rf"\b{re.escape(keyword)}\s*!", post, re.IGNORECASE):
          score += 2

    if len(found_keywords) >= 2:
        score += 2

    letters = re.sub(r"[^a-zA-Z]", "", post)
    if letters and letters.isupper():
      score += 1

    if score > 0:
      matches[post_id] = {
          "score": score,
          "keywords": found_keywords,
          "post": post
      }
      filtered_posts.append(post_id)

  print(f"\nTotal matches: {len(matches)}")
  print('-' * 60)

  for post_id, result in matches.items():
    score = result['score']
    found_keywords = result['keywords']
    postTxt = result['post'] # i think we can access the post normally but ehhhh

    match score:
      case x if 1 <= x <= 2:
        color = ANSIColor.GREEN
        risk_lvl = "Low"
      case x if 3 <= x <= 4:
        color = ANSIColor.YELLOW
        risk_lvl = " Medium"
      case x if x >= 5:
        color = ANSIColor.RED
        risk_lvl = "High"
      case _:
        color = ANSIColor.RESET
        risk_lvl = "None"
    
    # post, matched keyword(s), risk score, and risk classification
    formattedTxt = ANSIColor.format_color(
        f"{postTxt}\n\t> Words found: {", ".join(found_keywords)}| Risk: {risk_lvl} ({score})", color=color
    )

    print(formattedTxt)
    print('---')

  total = len(loaded_data)
  count_flagged = len(matches)
  print(f"Flagged Posts {count_flagged}/{total} ({int((count_flagged/total)*100)})%")

  total_score = 0
  for entry in matches.values():
    total_score += entry['score']
  print(f"Score average: {total_score}/{total}")

  print(f"Top 3 Highest Scores:\n{"-" * 50}")
  top_three = sorted(matches.items(), key=lambda x: x[1]['score'], reverse=True)[:3]
  for post_id, data in top_three:
    print(f"Post ID: {post_id}")
    print(f"Score: {data['score']}")
    print(f"Keywords: {data['keywords']}")
    print(f"Post: {data['post']}")
    print("-" * 50)
  

def save_log(frame:pd.DataFrame):
  '''
    Saves the given DataFrame to a CSV file. If the user provides a filename without an extension, it defaults to .csv. 
    If the file already exists, it appends a number to the filename to avoid overwriting.
  '''
  baseName = input("What do you want to name the outputted csv file?")
  base, ext = os.path.splitext(baseName)
  
  if ext != "":
    new_name = f'{base}{ext}'
  else:
    new_name = f"{base}.csv"
  
  if os.path.exists(new_name):
    count = 1
    new_name = f"{baseName}_{count}.csv"
    while os.path.exists(new_name):
      count += 1
      new_name = f"{baseName}_{count}.csv"
  frame.to_csv(new_name, index=False)
  print(f"Saved to {new_name}")
  handle_menu()
    

  
def gen_report():
  '''
    Generates a report by getting the scanned data, and redacting any keywords found in the posts.
    Calls for the program to save the CSV.
  '''
  global loaded_data
  global filtered_posts
  global matches

  new_cleaned_data = loaded_data.copy() # copy data

  if filtered_posts is None or len(filtered_posts) == 0:
    print("You don't have any posts filtered!")
    choice = input('Do you want to scan your posts? (Y/n)').strip().lower()
    if choice == 'y':
      analyze_data()
    else:
      handle_menu()
      return

  for post_id in filtered_posts:
    try:
      post = loaded_data.iloc[post_id]['post']

      detected_keywords = matches[post_id]['keywords']

      cleanedOutput = post
      for word in detected_keywords:
        pattern = rf"\b{re.escape(word)}\b"
        cleanedOutput = re.sub(pattern, '[redacted]', cleanedOutput, flags=re.IGNORECASE)
        new_cleaned_data.loc[post_id, 'post'] = cleanedOutput
      
  
    except Exception as e:
      print(f'oops i messed up on post {post_id} ({e})')
  save_log(new_cleaned_data)

def exit_program():
  '''
    Flags the program to exit.
  '''
  global exitProgram
  exitProgram = True


def handle_menu(is_help_menu=False):
    '''
        Handles the menu system by reading menu.json and displaying the options.
        If the user selects an option, it calls the corresponding function found in `func_name`
        If this doesn't exist, it will print an error message.
    '''

    if exitProgram:
      return

    with open('menu.json', 'r') as f:
        menu_data = json.load(f)['data']

    print("=== MENU ===")
    for index, item in enumerate(menu_data, start=1):
        print(f"{index}. {item['desc' if is_help_menu else 'action_name']}")

    choice = input("Select an option (1-{}): ".format(len(menu_data)))

    if choice.isdigit() and 1 <= int(choice) <= len(menu_data):
        selected_action = menu_data[int(choice) - 1]
        function_name = selected_action['func_name']
        if function_name in globals():
            globals()[function_name]()
        else:
            print(f"Function '{function_name}' not found.")

    if choice.lower() == 'h' or choice.lower() == 'help':
        handle_menu(is_help_menu=not is_help_menu)


def main():
    while True:
      handle_menu(is_help_menu=False)
      if exitProgram:
        break
    print("Goodbye!")

if __name__ == "__main__":
    main()