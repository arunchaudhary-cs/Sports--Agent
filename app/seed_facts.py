"""
seed_facts.py
-------------
Small starter set of STABLE historical sports facts used to seed the
ChromaDB collection on first run. Extend this list freely — it's the
"vector DB" half of the retrieval strategy (web_search.py covers the
fast-changing half).
"""

SEED_FACTS = [
    {"sport": "Cricket", "text": "India won the ICC Cricket World Cup in 1983, 2011, and were champions again in 2023 T20 World Cup era discussions; the 2011 title was won on home soil at Wankhede Stadium, Mumbai."},
    {"sport": "Cricket", "text": "Sachin Tendulkar holds the record for most international centuries in cricket history, with 100 centuries across Tests and ODIs."},
    {"sport": "Cricket", "text": "The fastest recorded delivery in cricket was bowled by Shoaib Akhtar at 161.3 km/h against England in the 2003 World Cup."},
    {"sport": "Football", "text": "Lionel Messi has won the Ballon d'Or award a record eight times as of his career milestones through 2023."},
    {"sport": "Football", "text": "The FIFA World Cup is held every four years; Brazil has won the tournament a record five times (1958, 1962, 1970, 1994, 2002)."},
    {"sport": "Football", "text": "Cristiano Ronaldo is widely regarded as one of the top all-time goal scorers in football history across club and international competitions."},
    {"sport": "Tennis", "text": "Novak Djokovic, Rafael Nadal, and Roger Federer are collectively known as the 'Big Three' of men's tennis for their dominance in Grand Slam titles during the 2000s-2020s."},
    {"sport": "Tennis", "text": "Wimbledon is the oldest tennis tournament in the world, first held in 1877, and is the only Grand Slam played on grass courts."},
    {"sport": "Badminton", "text": "PV Sindhu became the first Indian woman to win an Olympic silver medal in badminton, at the 2016 Rio Olympics, and later won bronze at Tokyo 2020."},
    {"sport": "Badminton", "text": "The BWF World Championships is badminton's premier individual event, held annually except in Olympic years."},
    {"sport": "Basketball", "text": "Michael Jordan won six NBA championships with the Chicago Bulls in the 1990s and is widely considered one of the greatest basketball players of all time."},
    {"sport": "Basketball", "text": "The NBA was founded in 1946 and currently consists of 30 teams across the United States and Canada."},
]

