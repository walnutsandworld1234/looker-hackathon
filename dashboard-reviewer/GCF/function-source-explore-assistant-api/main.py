
# MIT License

# Copyright (c) 2023 Looker Data Sciences, Inc.

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import json
import hmac
from flask import Flask, request, Response, jsonify
from flask_cors import CORS
import functions_framework
import vertexai
from vertexai.preview.generative_models import GenerativeModel, GenerationConfig
from vertexai.language_models import CodeGenerationModel
import logging

from vertexai.generative_models import (
    GenerationConfig,
    GenerativeModel,
    HarmBlockThreshold,
    HarmCategory,
    Part,
)

logging.basicConfig(level=logging.INFO)


# Initialize the Vertex AI
project = os.environ.get("PROJECT", "best-hack-427512")
location = os.environ.get("REGION", "us-central1")
vertex_cf_auth_token = os.environ.get("VERTEX_CF_AUTH_TOKEN")
model_name = os.environ.get("MODEL_NAME", "gemini-1.0-pro-001")

vertexai.init(project=project, location=location)

def get_response_headers(request):
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, X-Signature"
    }
    return headers


def has_valid_signature(request):
    signature = request.headers.get("X-Signature")
    if signature is None:
        return False

    # Validate the signature
    secret = vertex_cf_auth_token.encode("utf-8")
    print('I am here', secret)
    # request_data = request.get_data()
    hmac_obj = hmac.new(secret, ''.encode("utf-8"), "sha256")
    expected_signature = hmac_obj.hexdigest()

    return hmac.compare_digest(signature, expected_signature)

def generate_dashboard_response(contents, parameters=None, model_name="gemini-1.5-flash"):
    try:

        # Convert LookML data to JSON
        lookml_json = json.dumps(contents)

        # Generate prompt for the language model
        #prompt = f"You are a Data Analyst reviewing a Looker dashboard for which you are given the LookML file. Here are the rules to follow: Identify all titles (seen as - title) that do not have clear and descriptive names.Point out any filters whose names are ambigious. List the number of number of listen values for each title. Are there tiles with different number of listen values? Are there any tiles that could benefit from conditional formatting?Evaluate if the chosen visualization types are the best fit for the data being represented. Are there any metrics that are missing?Check if any fields have merged_queries. Are there any abbreviations in the - title or - dimension or - measures field that are not defined at the top, and can't be understood easily? Only highlight things that need improvement.\n\n{lookml_json}"

        # Load the model (replace with your model's ID)
        #model = CodeGenerationModel.from_pretrained("gemini-1.0-pro")
        MODEL_ID = "gemini-1.5-flash-001"  # @param {type:"string"}

        model = GenerativeModel(MODEL_ID)

        example_model = GenerativeModel(
            MODEL_ID,
            system_instruction=[
                "You are a Data Analyst reviewing a Looker dashboard for which you are given the LookML file. Here are the rules to follow: Identify all titles (seen as - title) that do not have clear and descriptive names.Point out any filters whose names are ambigious. List the number of number of listen values for each title. Are there tiles with different number of listen values? Are there any tiles that could benefit from conditional formatting?Evaluate if the chosen visualization types are the best fit for the data being represented. Are there any metrics that are missing?Check if any fields have merged_queries. Are there any abbreviations in the - title or - dimension or - measures field that are not defined at the top, and can't be understood easily? Only highlight things that need improvement.",
            ],
        )

        # Set model parameters
        generation_config = GenerationConfig(
            temperature=0.9,
            top_p=1.0,
            top_k=32,
            candidate_count=1,
            max_output_tokens=8192,
        )


        # Set safety settings
        safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
        }


        prompt = f"{lookml_json}"

        # Generate response with temperature setting
        #response = model.predict(prompt, temperature=0.0)  # Adjust temperature as needed (0.0 - 1.0)


        # Set contents to send to the model
        contents = [prompt]
        # Prompt the model to generate content
        response = example_model.generate_content(
            contents,
            generation_config=generation_config,
            safety_settings=safety_settings,
        )
        return response.text  # Return response as JSON

    except Exception as e:
        return jsonify({"error": str(e)}), 500

#    # Define default parameters
#     default_parameters = {
#         "temperature": 0.2,
#         "max_output_tokens": 500,
#         "top_p": 0.8,
#         "top_k": 40
#     }

#     # Override default parameters with any provided in the request
#     if parameters:
#         default_parameters.update(parameters)

#     # instantiate gemini model for prediction
#     model = GenerativeModel(model_name)

#     # make prediction to generate Looker Explore URL
#     response = model.generate_content(
#         contents=contents,
#         generation_config=GenerationConfig(
#             temperature=default_parameters["temperature"],
#             top_p=default_parameters["top_p"],
#             top_k=default_parameters["top_k"],
#             max_output_tokens=default_parameters["max_output_tokens"],
#             candidate_count=1
#         )
#     )

#     # grab token character count metadata and log
#     metadata = response.__dict__['_raw_response'].usage_metadata

#     # Complete a structured log entry.
#     entry = dict(
#         severity="INFO",
#         message={"request": contents, "response": response.text,
#                  "input_characters": metadata.prompt_token_count, "output_characters": metadata.candidates_token_count},
#         # Log viewer accesses 'component' as jsonPayload.component'.
#         component="explore-assistant-metadata",
#     )
#     logging.info(entry)
    # return response.text


# Flask app for running as a web server
def create_flask_app():
    app = Flask(__name__)
    CORS(app)

    @app.route("/", methods=["POST", "OPTIONS"])
    def base():
        if request.method == "OPTIONS":
            return handle_options_request(request)

        incoming_request = request.get_json()
        print(incoming_request)
        contents = incoming_request.get("lookml")
        parameters = incoming_request.get("parameters")
        if contents is None:
            return "Missing 'contents' parameter", 400

        if not has_valid_signature(request):
            return "Invalid signature", 403

        response_text = generate_dashboard_response(contents, parameters)

        return response_text, 200, get_response_headers(request)

    return app


# Function for Google Cloud Function
@functions_framework.http
def cloud_function_entrypoint(request):
    if request.method == "OPTIONS":
        return handle_options_request(request)

    incoming_request = request.get_json()
    contents = incoming_request.get("lookml")
    parameters = incoming_request.get("parameters")
    if contents is None:
        return "Missing 'contents' parameter", 400

    response_text = generate_dashboard_response(contents, parameters)

    return response_text, 200, get_response_headers(request)


def handle_options_request(request):
    return "", 204, get_response_headers(request)


# Determine the running environment and execute accordingly
if __name__ == "__main__":
    # Detect if running in a Google Cloud Function environment
    if os.environ.get("FUNCTIONS_FRAMEWORK"):
        # The Cloud Function entry point is defined by the decorator, so nothing is needed here
        pass
    else:
        app = create_flask_app()
        app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
