# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import vertexai
from vertexai.generative_models import GenerativeModel, Part, Image, HarmCategory, HarmBlockThreshold
import base64
from config import Config

class AIManager:
    def __init__(self):
        vertexai.init(project=Config.PROJECT_ID, location=Config.LOCATION)
        # Using Gemini 2.5 Flash for speed/cost efficiency in production validation
        self.model = GenerativeModel("gemini-2.5-flash")

    def validate_submission(self, image_bytes, expected_description):
        """
        Validates the user uploaded image against the owner's description.
        Returns: (bool: is_approved, str: comment)
        """
        try:
            prompt = f"""
            You are a code result validation judge.
            
            Task: Compare the provided screenshot against the following requirement description.
            Requirement Description: "{expected_description}"
            
            Instructions:
            1. Analyze the image to see if it visually demonstrates the requirement.
            2. Be reasonbly strict but fair. If the image is unrelated, blurry, or clearly wrong, reject it.
            3. If it matches contextually (not exactly 1 to 1), approve it.
            
            Output format:
            Start your response with exactly "APPROVED" or "REJECTED".
            Follow it with a short, constructive one-sentence reason.
            Example: "REJECTED: The screenshot shows a terminal error instead of the expected success message."
            """
            
            # Configure safety settings to block only high probability of harm
            # This reduces false positives for benign code screenshots
            safety_settings = {
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            }

            image_part = Part.from_data(data=image_bytes, mime_type="image/png")
            
            # Increased max_output_tokens from 100 to 1024 to accommodate thought process + response
            responses = self.model.generate_content(
                [prompt, image_part],
                generation_config={"max_output_tokens": 1024, "temperature": 0.2},
                safety_settings=safety_settings
            )
            
            response_text = responses.text.strip()
            
            # Parse logic
            if response_text.upper().startswith("APPROVED"):
                return True, response_text.replace("APPROVED", "").strip().lstrip(": ")
            else:
                return False, response_text.replace("REJECTED", "").strip().lstrip(": ")

        except Exception as e:
            # Explicitly returning the error message for debugging
            print(f"AI Error: {e}")
            return False, f"System Error: {str(e)}"