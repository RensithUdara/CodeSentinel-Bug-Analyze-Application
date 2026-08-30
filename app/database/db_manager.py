"""
SQLite database manager.
"""
import sqlite3
import os
from typing import List, Dict, Any, Optional


class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None

    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def initialize(self):
        self.connect()
        cursor = self.conn.cursor()
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS projects (
                project_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                path TEXT UNIQUE NOT NULL,
                description TEXT,
                primary_language TEXT,
                git_repo TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS analysis_runs (
                analysis_id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                commit_hash TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                quality_score REAL,
                security_score REAL,
                complexity_score REAL,
                maintainability_score REAL,
                duplication_score REAL,
                architecture_score REAL,
                technical_debt REAL,
                FOREIGN KEY (project_id) REFERENCES projects(project_id)
            );

            CREATE TABLE IF NOT EXISTS files (
                file_id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id INTEGER NOT NULL,
                path TEXT NOT NULL,
                language TEXT,
                loc INTEGER,
                comment_lines INTEGER,
                function_count INTEGER,
                class_count INTEGER,
                complexity REAL,
                maintainability REAL,
                FOREIGN KEY (analysis_id) REFERENCES analysis_runs(analysis_id)
            );

            CREATE TABLE IF NOT EXISTS issues (
                issue_id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id INTEGER NOT NULL,
                file_id INTEGER,
                type TEXT,
                category TEXT,
                severity TEXT,
                line_number INTEGER,
                message TEXT,
                metric_value REAL,
                threshold REAL,
                recommendation TEXT,
                status TEXT DEFAULT 'Open',
                FOREIGN KEY (analysis_id) REFERENCES analysis_runs(analysis_id),
                FOREIGN KEY (file_id) REFERENCES files(file_id)
            );

            CREATE TABLE IF NOT EXISTS duplicates (
                duplicate_id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id INTEGER NOT NULL,
                file_a TEXT,
                file_b TEXT,
                similarity REAL,
                start_line_a INTEGER,
                end_line_a INTEGER,
                start_line_b INTEGER,
                end_line_b INTEGER,
                FOREIGN KEY (analysis_id) REFERENCES analysis_runs(analysis_id)
            );
        """)
        self.conn.commit()
        self.close()

    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        self.connect()
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        self.conn.commit()
        return cursor

    def fetchall(self, query: str, params: tuple = ()) -> List[sqlite3.Row]:
        self.connect()
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        self.close()
        return rows

    def fetchone(self, query: str, params: tuple = ()) -> Optional[sqlite3.Row]:
        self.connect()
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        row = cursor.fetchone()
        self.close()
        return row
