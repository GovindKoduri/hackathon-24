import ssl
import pymongo
from pymongo import MongoClient
from flask import Flask, request, jsonify
from openai import AzureOpenAI

app = Flask(__name__)

client = AzureOpenAI(
    api_key = "60115cf02de24a04892bb9212af45df6",
    api_version = "2023-12-01-preview",
    azure_endpoint = "https://talosai.openai.azure.com/"
)

context = [{"role": "system",
            "content": "You are a helpful chatbot that is going to recommend clothing products based on user preferences."}]

def get_chat_completion_response(user_query):

    username = "John Doe"
    
    preferences = user_preferences(username)

    prompt_with_user_preferences = f"{user_query} {preferences}"

    print(prompt_with_user_preferences)

    context.append({"role": "user", "content": prompt_with_user_preferences})

    # Specify the GPT model for chat completion (gpt-3.5-turbo)
    model_engine = "got-35"

    response = client.chat.completions.create(model=model_engine,  messages=context)

    # Extract the generated text from the ChatGPT response
    generated_response = response.choices[0].message.content

    context.append({"role": "assistant", "content": generated_response})

    return generated_response


def user_preferences(username):
    mongo_url = "mongodb+srv://AIAvengers:Hackathon2024@hackathon-2024.mongocluster.cosmos.azure.com/?tlsAllowInvalidCertificates=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000"
    database = "hackathon_db_2024"
    collection_name = "customer_history"

    client = pymongo.MongoClient(mongo_url)
    db = client[database]
    collection = db[collection_name]
    documents = collection.find_one({'user.name': username})
    client.close()

    errorMessage = " {} User not found".format(username)

    if documents:
        return str(documents['purchasedProducts'])
    else:
        return jsonify({"Error ": errorMessage}), 404


@app.route('/assistantMessage', methods=['POST'])
def assistant_message():
    user_query = request.json.get('user_query', '')
    if not user_query:
        return jsonify({"error": "User query not provided"}), 400

    response = get_chat_completion_response(user_query)
    return response;



@app.route('/api/user/<username>', methods=['GET'])
def get_user_data_by_username(username):
    mongo_url = "mongodb+srv://AIAvengers:Hackathon2024@hackathon-2024.mongocluster.cosmos.azure.com/?tlsAllowInvalidCertificates=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000"
    database = "hackathon_db_2024"
    collection_name = "customer_history"

    client = pymongo.MongoClient(mongo_url)
    db = client[database]
    collection = db[collection_name]
    documents = collection.find_one({'user.name': username})
    client.close()

    errorMessage = " {} User not found".format(username)

    if documents:
        return str(documents['purchasedProducts'])
    else:
        return jsonify({"Error ": errorMessage}), 404

    
if __name__ == '__main__':
    app.run(debug=True)