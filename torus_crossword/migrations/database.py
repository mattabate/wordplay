from sqlalchemy.orm import sessionmaker
from sqlalchemy import not_
from migrations.schema import Word, ReviewStatus, engine
import datetime

# Create a session factory
Session = sessionmaker(bind=engine)


def get_non_rejected_words():
    """
    Retrieve all words where review_status is not REJECTED.

    Returns:
        List[str]: A list of words with review_status not equal to REJECTED.
    """
    # Create a new session
    session = Session()
    try:
        # Query the database for words where review_status is not REJECTED
        results = (
            session.query(Word.word)
            .filter(not_(Word.review_status == ReviewStatus.REJECTED))
            .all()
        )

        # Extract the words from the query results
        words = [result.word for result in results]

        return words
    finally:
        # Close the session
        session.close()


def get_words_reviewed():
    """
    Retrieve all words where review_status is not NOT_REVIEWED.

    Returns:
        List[str]: A list of words with review_status not equal to NOT_REVIEWED.
    """
    # Create a new session
    session = Session()
    try:
        # Query the database for words where review_status is not NOT_REVIEWED
        results = (
            session.query(Word.word)
            .filter(not_(Word.review_status == ReviewStatus.NOT_REVIEWED))
            .all()
        )

        # Extract the words from the query results
        words = [result.word for result in results]

        return words
    finally:
        # Close the session
        session.close()


def change_word_review(word, review_status):
    """
    Update the review_status of a word in the database.

    Args:
        word (str): The word to update.
        review_status (ReviewStatus): The new review status for the word.
    """
    # Create a new session
    session = Session()
    try:
        # Query the database for the word
        word_entry = session.query(Word).filter(Word.word == word).first()

        # Update the review_status of the word
        word_entry.review_status = review_status
        word_entry.last_updated = datetime.datetime.now()

        # Commit the changes to the database
        session.commit()
    finally:
        # Close the session
        session.close()


def get_word_status(word):
    """
    Retrieve the review status of a given word.

    Args:
        word (str): The word whose status is to be retrieved.

    Returns:
        str: The review status of the word, or None if the word is not found.
    """
    # Create a new session
    session = Session()
    try:
        # Query the database for the review status of the given word
        result = session.query(Word.review_status).filter(Word.word == word).first()

        # Return the review status if found, or None otherwise
        return result[0].value if result else None
    finally:
        # Close the session
        session.close()


def get_word(word):
    """
    Retrieve the Word object for a given word.

    Args:
        word (str): The word to retrieve.

    Returns:
        Word: The Word object if found, or None if the word does not exist.
    """
    # Create a new session
    session = Session()
    try:
        # Query the database for the word
        result = session.query(Word).filter(Word.word == word).first()

        return result
    finally:
        # Close the session
        session.close()


# get all words of a specific review status
def get_words_by_status(status):
    """
    Retrieve all words with a specific review status.

    Args:
        status (ReviewStatus): The review status to filter by.

    Returns:
        List[str]: A list of words with the specified review status.
    """
    # Create a new session
    session = Session()
    try:
        # Query the database for words with the specified review status
        results = session.query(Word.word).filter(Word.review_status == status).all()

        # Extract the words from the query results
        words = [result.word for result in results]

        return words
    finally:
        # Close the session
        session.close()


def get_words_by_length(length):
    """
    Retrieve all words of a specific length.

    Args:
        length (int): The length of the words to retrieve.

    Returns:
        List[str]: A list of words with the specified length.
    """
    # Create a new session
    session = Session()
    try:
        # Query the database for words with the specified length
        results = session.query(Word.word).filter(Word.length == length).all()

        # Extract the words from the query results
        words = [result.word for result in results]

        return words
    finally:
        # Close the session
        session.close()


# given a list of words, which ones dont have an approved status
def words_not_approved_from_list(list_words: list[str]):
    """
    Retrieve all words from a list that do not have an APPROVED status.

    Args:
        list_words (List[str]): A list of words to check.

    Returns:
        List[str]: A list of words that do not have an APPROVED status.
    """
    # Create a new session
    session = Session()
    try:
        # Query the database for words that are not approved
        results = (
            session.query(Word.word)
            .filter(Word.word.in_(list_words))
            .filter(Word.review_status != ReviewStatus.APPROVED)
            .all()
        )

        # Extract the words from the query results
        words = [result.word for result in results]

        return words
    finally:
        # Close the session
        session.close()


def update_matt_score(word: str, matt_score: float):
    """
    Update the Matt score of a word in the database.

    Args:
        word (str): The word to update.
        matt_score (float): The new Matt score for the word.
    """
    # Create a new session
    session = Session()
    try:
        # Query the database for the word
        word_entry = session.query(Word).filter(Word.word == word).first()

        # Update the Matt score of the word
        word_entry.matt_score = matt_score

        # Commit the changes to the database
        session.commit()
    finally:
        # Close the session
        session.close()


def get_word_world_score(word: str):
    """
    Retrieve the world score of a given word.

    Args:
        word (str): The word whose world score is to be retrieved.

    Returns:
        float: The world score of the word.
    """
    # Create a new session
    session = Session()
    try:
        # Query the database for the world score of the given word
        result = session.query(Word.world_score).filter(Word.word == word).first()

        # Return the world score if found
        return result[0]
    finally:
        # Close the session
        session.close()
