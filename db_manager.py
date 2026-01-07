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

from google.cloud import bigquery
from config import Config
import random
import string
import datetime

class DBManager:
    def __init__(self):
        self.client = bigquery.Client(project=Config.PROJECT_ID)
        self.dataset = f"{Config.PROJECT_ID}.{Config.BQ_DATASET}"

    def check_credentials(self, username, password):
        query = f"""
            SELECT role FROM `{self.dataset}.login`
            WHERE username = @username AND password = @password
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("username", "STRING", username),
                bigquery.ScalarQueryParameter("password", "STRING", password)
            ]
        )
        result = self.client.query(query, job_config=job_config).result()
        for row in result:
            return row.role
        return None

    def create_season_session(self, season_num, s_start, s_end, sub_end, sess_num, sess_title, link, step, desc, img_b64):
        check_query = f"""
            SELECT 1 FROM `{self.dataset}.seasons_sessions`
            WHERE season_number = @sn AND session_number = @ssn
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("sn", "INT64", season_num),
                bigquery.ScalarQueryParameter("ssn", "INT64", sess_num)
            ]
        )
        if self.client.query(check_query, job_config=job_config).result().total_rows > 0:
            return False, "Session already exists for this season."

        rows = [{
            "season_number": season_num, "season_start_date": s_start, "season_end_date": s_end,
            "submission_end_date": sub_end, "session_number": sess_num, "session_title": sess_title,
            "codelab_link": link, "step_number": step, "result_description": desc,
            "sample_screenshot_base64": img_b64
        }]
        errors = self.client.insert_rows_json(f"{self.dataset}.seasons_sessions", rows)
        return (True, "Success") if not errors else (False, errors)

    def get_leaderboard(self):
        query = f"""
            SELECT 
                username, 
                COUNT(*) as approved_count,
                MAX(submission_timestamp) as last_success_time
            FROM `{self.dataset}.developers`
            WHERE validation_result = 'APPROVED'
            GROUP BY username
            ORDER BY approved_count DESC, last_success_time ASC
        """
        return self.client.query(query).result()

    def get_developer_stats(self, username):
        query = f"""
            SELECT 
                COUNT(DISTINCT season_number) as total_seasons,
                COUNTIF(validation_result = 'APPROVED') as lab_score
            FROM `{self.dataset}.developers`
            WHERE username = @u
        """
        config = bigquery.QueryJobConfig(
            query_parameters=[bigquery.ScalarQueryParameter("u", "STRING", username)]
        )
        results = list(self.client.query(query, job_config=config).result())
        if results:
            return results[0]
        return None

    def generate_bulk_credentials(self, count):
        new_creds_map = {} 
        while len(new_creds_map) < count:
            needed = count - len(new_creds_map)
            for _ in range(needed):
                uname = 'dev_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
                while uname in new_creds_map:
                     uname = 'dev_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
                pwd = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
                new_creds_map[uname] = pwd
            
            candidates = list(new_creds_map.keys())
            query = f"""
                SELECT username FROM `{self.dataset}.login`
                WHERE username IN UNNEST(@candidates)
            """
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ArrayQueryParameter("candidates", "STRING", candidates)
                ]
            )
            result = self.client.query(query, job_config=job_config).result()
            collisions = {row.username for row in result}
            if not collisions:
                break
            for bad_user in collisions:
                del new_creds_map[bad_user]
            
        rows_to_insert = [{"username": u, "password": p, "role": "DEVELOPER"} for u, p in new_creds_map.items()]
        errors = self.client.insert_rows_json(f"{self.dataset}.login", rows_to_insert)
        
        if errors:
            print(f"BigQuery Insert Errors: {errors}")
            return []
            
        return [{"username": u, "password": p} for u, p in new_creds_map.items()]

    def get_active_season(self):
        today = datetime.date.today().isoformat()
        query = f"""
            SELECT DISTINCT season_number 
            FROM `{self.dataset}.seasons_sessions`
            WHERE season_start_date <= '{today}' AND season_end_date >= '{today}'
            LIMIT 1
        """
        res = self.client.query(query).result()
        for row in res:
            return row.season_number
        return None

    def get_sessions_for_season(self, season_num):
        query = f"""
            SELECT session_number, session_title, result_description
            FROM `{self.dataset}.seasons_sessions`
            WHERE season_number = @sn
            ORDER BY session_number
        """
        config = bigquery.QueryJobConfig(
            query_parameters=[bigquery.ScalarQueryParameter("sn", "INT64", season_num)]
        )
        return list(self.client.query(query, job_config=config).result())

    def get_developer_status(self, username, season, session):
        query = f"""
            SELECT validation_result, retry_count, request_intervention, validation_comment
            FROM `{self.dataset}.developers`
            WHERE username = @u AND season_number = @sn AND session_number = @ssn
        """
        config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("u", "STRING", username),
                bigquery.ScalarQueryParameter("sn", "INT64", season),
                bigquery.ScalarQueryParameter("ssn", "INT64", session)
            ]
        )
        res = list(self.client.query(query, job_config=config).result())
        return res[0] if res else None

    def submit_attempt(self, username, password, season, session, result, comment, retry_count=1, intervention=False):
        """
        Inserts a new submission attempt.
        Removed UPDATE logic to enforce immutable history for this use case.
        """
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        row = {
            "username": username, "password": password, 
            "season_number": season, "session_number": session,
            "validation_result": result, "validation_comment": comment,
            "retry_count": retry_count, 
            "request_intervention": intervention,
            "submission_timestamp": timestamp
        }
        self.client.insert_rows_json(f"{self.dataset}.developers", [row])
        return True