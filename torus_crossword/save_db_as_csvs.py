# load database.bs and save all tables as csvs in csv_data/

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from migrations.schema import engine, Base, Word
import os

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# save Word table as csv
words = session.query(Word).all()
df = pd.DataFrame([word.__dict__ for word in words])
df.drop("_sa_instance_state", axis=1, inplace=True)
# put the columns in the right order
df = df[["word", "world_score", "matt_score", "review_status", "last_updated", "clues"]]
df.to_csv("csv_data/words.csv", index=False)
