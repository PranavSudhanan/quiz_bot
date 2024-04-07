from .constants import BOT_WELCOME_MESSAGE, PYTHON_QUESTION_LIST


def generate_bot_responses(message, session):
    bot_responses = []

    current_question_id = session.get("current_question_id")

    if current_question_id is None:
        # If there's no current question ID, it's the first interaction or after resetting the quiz, show the welcome message along with the first question and its options
        session["current_question_id"] = 0
        session["answers"] = {}  # Clear the answers when resetting the quiz
        session.save()
        # bot_responses.append(BOT_WELCOME_MESSAGE)
        first_question_info = PYTHON_QUESTION_LIST[0]
        bot_responses.append(first_question_info["question_text"])
        bot_responses.extend(first_question_info["options"])
        return bot_responses

    success, error = record_current_answer(message, current_question_id, session)

    if not success:
        return [error]

    next_question, next_question_id = get_next_question(current_question_id)

    if next_question:
        # Get the question text and options
        question_info = PYTHON_QUESTION_LIST[next_question_id]
        question_text = question_info["question_text"]
        options = question_info["options"]

        # Construct the response with the question and options
        bot_responses.append(question_text)
        bot_responses.extend(options)
    else:
        final_response = generate_final_response(session)
        bot_responses.append(final_response)

    session["current_question_id"] = next_question_id
    session.save()

    return bot_responses


def record_current_answer(answer, current_question_id, session):
    '''
    Validates and stores the answer for the current question to django session.
    '''
    if current_question_id is not None and 0 <= current_question_id < len(PYTHON_QUESTION_LIST):
        question = PYTHON_QUESTION_LIST[current_question_id]
        correct_answer = question["answer"]
        if answer == correct_answer:
            # Store the answer in session
            session["answers"][current_question_id] = True
        else:
            # Store the incorrect answer in session
            session["answers"][current_question_id] = False
        return True, ""
    else:
        return False, "Invalid current question id"


def get_next_question(current_question_id):
    '''
    Fetches the next question from the PYTHON_QUESTION_LIST based on the current_question_id.
    '''
    if current_question_id is None:
        next_question_id = 0
    else:
        next_question_id = current_question_id + 1

    if next_question_id < len(PYTHON_QUESTION_LIST):
        next_question_info = PYTHON_QUESTION_LIST[next_question_id]
        next_question = next_question_info["question_text"]
        return next_question, next_question_id
    else:
        return None, None


def generate_final_response(session):
    '''
    Creates a final result message including a score based on the answers
    by the user for questions in the PYTHON_QUESTION_LIST.
    '''
    total_questions = len(PYTHON_QUESTION_LIST)
    correct_answers = sum(session.get("answers", {}).values())
    score = (correct_answers / total_questions) * 100 if total_questions != 0 else 0
    final_response = f"You answered {correct_answers}/{total_questions} questions correctly. Your score is {score:.2f}%."
    return final_response
