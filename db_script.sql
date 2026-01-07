-- Copyright 2025 Google LLC
--
-- Licensed under the Apache License, Version 2.0 (the "License");
-- you may not use this file except in compliance with the License.
-- You may obtain a copy of the License at
--
--      http://www.apache.org/licenses/LICENSE-2.0
--
-- Unless required by applicable law or agreed to in writing, software
-- distributed under the License is distributed on an "AS IS" BASIS,
-- WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
-- See the License for the specific language governing permissions and
-- limitations under the License.

-- BigQuery Setup Script for Code Vipassana Validation App

-- 1. Create Dataset (if running manually, otherwise the tables below assume dataset exists)
-- CREATE SCHEMA IF NOT EXISTS `cv_validation`;

-- 2. Table: login
-- Stores user credentials and roles.
CREATE TABLE IF NOT EXISTS `cv_validation.login` (
    username STRING NOT NULL,
    password STRING NOT NULL,
    role STRING NOT NULL -- 'OWNER' or 'DEVELOPER'
);

-- 3. Table: seasons_sessions
-- Stores configuration for seasons and their specific sessions.
CREATE TABLE IF NOT EXISTS `cv_validation.seasons_sessions` (
    season_number INT64 NOT NULL,
    season_start_date DATE,
    season_end_date DATE,
    submission_end_date DATE,
    session_number INT64 NOT NULL,
    session_title STRING,
    codelab_link STRING,
    step_number INT64,
    result_description STRING,
    sample_screenshot_base64 STRING -- Storing sample image as base64 string for reference
);

-- 4. Table: developers
-- Stores submission attempts, validation results, and retry status.
CREATE TABLE IF NOT EXISTS `cv_validation.developers` (
    username STRING NOT NULL,
    password STRING, -- Snapshot of password used, per requirements
    season_number INT64 NOT NULL,
    session_number INT64 NOT NULL,
    validation_result STRING, -- 'APPROVED' or 'REJECTED'
    validation_comment STRING,
    retry_count INT64 DEFAULT 0,
    request_intervention BOOL DEFAULT FALSE, 
    submission_timestamp TIMESTAMP
);

-- 5. Insert Initial Owner
-- Insert a default owner to get started (You can change the password later)
INSERT INTO `cv_validation.login` (username, password, role)
VALUES ('*****', '***********', 'OWNER');