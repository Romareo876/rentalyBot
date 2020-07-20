import os
import dialogflow_v2 as dialogflow
project_id = os.getenv('DIALOGFLOW_PROJECT_ID')


session_client = dialogflow.SessionsClient()

def detect_intent_texts(text, session_id, language_code='en'):
    session = session_client.session_path(project_id, session_id)
    text_input = dialogflow.types.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.types.QueryInput(text=text_input)
    response = session_client.detect_intent(session=session, query_input=query_input)
    return response.query_result


def get_reply(query, session_id): #use userphone number as session id
    response = detect_intent_texts(query, session_id)
    return response.fulfillment_text #response form dialogflow

