import json
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.sqlite import insert
from schema import engine, Word, ReviewStatus
import datetime
import tqdm


# Create a session
Session = sessionmaker(bind=engine)
session = Session()


def populate_words_from_json(
    wordlist_json, words_approved_json, words_omitted_json, score_dict_json
):
    """Populate the words table from a JSON file."""
    try:
        # Load words from the JSON file
        with open(wordlist_json, "r") as file:
            words = json.load(file)

        with open(words_approved_json, "r") as file:
            approved_words = json.load(file)

        with open(words_omitted_json, "r") as file:
            omitted_words = json.load(file)

        with open(score_dict_json, "r") as file:
            score_dict = json.load(file)

        # Iterate over words and upsert them into the database
        for word_entry in tqdm.tqdm(words):
            review_status = ReviewStatus.NOT_REVIEWED
            if word_entry in approved_words:
                review_status = ReviewStatus.APPROVED
            elif word_entry in omitted_words:
                review_status = ReviewStatus.REJECTED

            world_score = None
            if word_entry in score_dict:
                world_score = score_dict[word_entry]

            stmt = insert(Word).values(
                word=word_entry,
                world_score=world_score,  # Column(Float, nullable=True)
                matt_score=None,  # Column(Float, nullable=True)
                review_status=review_status,  # Column(String, nullable=True)  # APPROVED, REJECTED, or NULL
                last_updated=datetime.datetime.now(),  # Placeholder for last_updates
                clues=None,  # Column(String, nullable=True)
            )
            session.execute(stmt)

        # Commit the session
        session.commit()
        print(f"Successfully populated the words table from {wordlist_json}")

    except Exception as e:
        session.rollback()
        print(f"Error occurred: {e}")

    finally:
        session.close()


if __name__ == "__main__":
    populate_words_from_json(
        wordlist_json="wordlist/word_list.json",
        words_approved_json="wordlist/words_approved.json",
        words_omitted_json="wordlist/words_omitted.json",
        score_dict_json="wordlist/scores_dict.json",
    )
