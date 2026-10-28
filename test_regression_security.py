"""
SkillPathAI - Phase A Security & Backend Reliability Regression Test Suite

Tests:
1. Missing Firebase token (401)
2. Invalid Firebase token (401)
3. Valid token accessing own profile (200)
4. Attempt to access another user's profile (403 BOLA/IDOR prevention)
5. Attempt to modify another user's profile (403 BOLA/IDOR prevention)
6. Unauthorized roadmap generation without token (401)
7. Roadmap generation for another user (403 BOLA/IDOR prevention)
8. Database diagnostic endpoint protects schema metadata (no version, database name, or table list)
9. AI service unconfigured/unavailable returns proper 503 (no server crash)
10. AI service timeout returns proper 504 (no HTTP 200 with error dict)
"""

import os
import sys

# Ensure backend directory is in sys.path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Setup test in-memory SQLite database before importing main app
from database.mysql import Base
from models.user import User
from models.profile import Profile
from models.assessment import Assessment
from models.roadmap import Roadmap
from models.topic import Topic
from models.progress import Progress
from models.quiz_result import QuizResult

test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Import app and patch SessionLocal to use SQLite for tests
import main
main.SessionLocal = TestingSessionLocal

from auth import verify_token
client = TestClient(main.app)


class TestSecurityAndReliability(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=test_engine)

    @classmethod
    def tearDownClass(cls):
        Base.metadata.drop_all(bind=test_engine)

    def setUp(self):
        # Reset dependency overrides and re-seed tables for each test
        main.app.dependency_overrides = {}
        Base.metadata.drop_all(bind=test_engine)
        Base.metadata.create_all(bind=test_engine)

        # Seed two distinct users and profiles for BOLA/IDOR testing
        db = TestingSessionLocal()
        try:
            self.user1 = User(
                user_id=1,
                name="Alice User",
                email="alice@example.com",
                firebase_uid="uid_alice_123",
                career_goal="Web Development"
            )
            self.user2 = User(
                user_id=2,
                name="Bob User",
                email="bob@example.com",
                firebase_uid="uid_bob_456",
                career_goal="Data Science"
            )
            db.add_all([self.user1, self.user2])
            db.commit()

            self.profile1 = Profile(
                profile_id=1,
                user_id=1,
                education="BS Computer Science",
                interests="React, Node",
                current_skills="HTML, CSS",
                skill_level="Beginner"
            )
            self.profile2 = Profile(
                profile_id=2,
                user_id=2,
                education="MS Data Science",
                interests="Machine Learning",
                current_skills="Python, SQL",
                skill_level="Advanced"
            )
            db.add_all([self.profile1, self.profile2])
            db.commit()
        finally:
            db.close()

    # 1. Missing Firebase token
    def test_missing_firebase_token(self):
        res = client.get("/profiles/1")
        self.assertEqual(res.status_code, 401)
        self.assertIn("detail", res.json())

    # 2. Invalid Firebase token
    def test_invalid_firebase_token(self):
        res = client.get("/profiles/1", headers={"Authorization": "Bearer invalid_token_xyz"})
        self.assertEqual(res.status_code, 401)
        self.assertIn("Invalid or expired", res.json()["detail"])

    # 3. Valid token accessing own profile
    def test_valid_token_access_own_profile(self):
        main.app.dependency_overrides[verify_token] = lambda: {
            "uid": "uid_alice_123",
            "email": "alice@example.com"
        }
        res = client.get("/profiles/1", headers={"Authorization": "Bearer mocked_token"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["user_id"], 1)
        self.assertEqual(data["education"], "BS Computer Science")

    # 4. Attempt to access another user's profile (403 BOLA/IDOR prevention)
    def test_access_another_user_profile_forbidden(self):
        # Authenticated as Alice (user_id=1)
        main.app.dependency_overrides[verify_token] = lambda: {
            "uid": "uid_alice_123",
            "email": "alice@example.com"
        }
        # Attempt to access Bob's profile (user_id=2)
        res = client.get("/profiles/2", headers={"Authorization": "Bearer mocked_token"})
        self.assertEqual(res.status_code, 403)
        self.assertIn("Forbidden", res.json()["detail"])

    # 5. Attempt to modify another user's profile (403 BOLA/IDOR prevention)
    def test_modify_another_user_profile_forbidden(self):
        # Authenticated as Alice (user_id=1)
        main.app.dependency_overrides[verify_token] = lambda: {
            "uid": "uid_alice_123",
            "email": "alice@example.com"
        }
        # Attempt to modify Bob's profile (user_id=2)
        res = client.patch(
            "/profiles/2",
            json={"education": "Hacked Degree"},
            headers={"Authorization": "Bearer mocked_token"}
        )
        self.assertEqual(res.status_code, 403)
        self.assertIn("Forbidden", res.json()["detail"])

        # Verify Bob's profile in database remains untouched
        db = TestingSessionLocal()
        try:
            bob = db.query(Profile).filter(Profile.user_id == 2).first()
            self.assertEqual(bob.education, "MS Data Science")
        finally:
            db.close()

    # 6. Unauthorized roadmap generation without token
    def test_unauthorized_roadmap_generation_missing_token(self):
        res = client.post("/generate-roadmap", json={
            "user_id": 1,
            "career_goal": "Web Dev",
            "current_skills": "HTML",
            "interests": "Frontend",
            "skill_level": "Beginner",
            "assessment_score": 75.0
        })
        self.assertEqual(res.status_code, 401)

    # 7. Roadmap generation for another user (403 BOLA/IDOR prevention)
    def test_roadmap_generation_for_another_user_forbidden(self):
        # Authenticated as Alice (user_id=1)
        main.app.dependency_overrides[verify_token] = lambda: {
            "uid": "uid_alice_123",
            "email": "alice@example.com"
        }
        # Attempt to generate roadmap for Bob (user_id=2)
        res = client.post("/generate-roadmap", json={
            "user_id": 2,
            "career_goal": "Data Science",
            "current_skills": "Python",
            "interests": "AI",
            "skill_level": "Advanced",
            "assessment_score": 90.0
        }, headers={"Authorization": "Bearer mocked_token"})
        self.assertEqual(res.status_code, 403)

        # Also test user-id route parameter
        res2 = client.post("/generate-roadmap/2", headers={"Authorization": "Bearer mocked_token"})
        self.assertEqual(res2.status_code, 403)

    # 8. Database diagnostic endpoint protects schema metadata
    def test_db_diagnostic_endpoint_does_not_leak_metadata(self):
        res = client.get("/db-test")
        # In test environment, it executes SELECT 1 against test DB
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data.get("status"), "ok")
        self.assertEqual(data.get("database"), "connected")
        # Verify sensitive metadata fields are NOT present
        self.assertNotIn("tables", data)
        self.assertNotIn("version", data)
        self.assertNotIn("database_name", data)

    # 9. AI service unconfigured/missing key returns proper 503 (no server crash)
    @patch.dict(os.environ, {"GEMINI_API_KEY": ""}, clear=False)
    def test_ai_service_unconfigured_returns_503(self):
        main.app.dependency_overrides[verify_token] = lambda: {
            "uid": "uid_alice_123",
            "email": "alice@example.com"
        }
        res = client.post(
            "/explain-topic",
            json={"topic_name": "Binary Trees", "skill_level": "Beginner"},
            headers={"Authorization": "Bearer mocked_token"}
        )
        self.assertEqual(res.status_code, 503)
        self.assertIn("not configured", res.json()["detail"].lower())

    # 10. AI service timeout returns proper 504 error code (never HTTP 200 with error dict)
    def test_roadmap_generation_timeout_returns_504(self):
        main.app.dependency_overrides[verify_token] = lambda: {
            "uid": "uid_alice_123",
            "email": "alice@example.com"
        }
        with patch("main.generate_roadmap", side_effect=Exception("Request timed out after 25s")):
            res = client.post(
                "/generate-roadmap",
                json={
                    "user_id": 1,
                    "career_goal": "Web Dev",
                    "current_skills": "HTML",
                    "interests": "Frontend",
                    "skill_level": "Beginner",
                    "assessment_score": 80.0
                },
                headers={"Authorization": "Bearer mocked_token"}
            )
            self.assertEqual(res.status_code, 504)
            self.assertIn("timed out", res.json()["detail"].lower())
            # Ensure it is NOT returning a 200 with an error object
            self.assertNotEqual(res.status_code, 200)

    # 11. Dashboard overview progress summary calculates 18/30 (60%) correctly with deduplication
    def test_dashboard_overview_progress_summary_with_completed_topics(self):
        main.app.dependency_overrides[verify_token] = lambda: {
            "uid": "uid_alice_123",
            "email": "alice@example.com"
        }
        db = TestingSessionLocal()
        try:
            # Create roadmap with 30 topics for User 1
            roadmap = Roadmap(roadmap_id=1, user_id=1, career_path="Web Development")
            db.add(roadmap)
            db.commit()

            topics = [
                Topic(topic_id=i, roadmap_id=1, topic_name=f"Topic {i}", sequence_no=i, status="Not Started")
                for i in range(1, 31)
            ]
            db.add_all(topics)
            db.commit()

            # Add 18 completed progress records (topics 1 to 18)
            progress_records = [
                Progress(user_id=1, topic_id=i, completion_percentage=100, status="Completed")
                for i in range(1, 19)
            ]
            # Add a duplicate record for topic 1 to verify deduplication
            progress_records.append(Progress(user_id=1, topic_id=1, completion_percentage=50, status="In Progress"))
            db.add_all(progress_records)
            db.commit()
        finally:
            db.close()

        res = client.get("/dashboard/overview", headers={"Authorization": "Bearer mocked_token"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("progress_summary", data)
        summary = data["progress_summary"]

        self.assertEqual(summary["completed_topics"], 18)
        self.assertEqual(summary["total_topics"], 30)
        self.assertEqual(summary["overall_percentage"], 60)
        self.assertEqual(summary["fraction"], "18/30")
        self.assertIsNotNone(summary["current_topic"])
        self.assertEqual(summary["current_topic"]["topic_id"], 19)

    # 12. Dashboard overview zero division safety when no topics exist
    def test_dashboard_overview_empty_roadmap_zero_division_safety(self):
        main.app.dependency_overrides[verify_token] = lambda: {
            "uid": "uid_alice_123",
            "email": "alice@example.com"
        }
        res = client.get("/dashboard/overview", headers={"Authorization": "Bearer mocked_token"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("progress_summary", data)
        summary = data["progress_summary"]

        self.assertEqual(summary["completed_topics"], 0)
        self.assertEqual(summary["total_topics"], 0)
        self.assertEqual(summary["overall_percentage"], 0)
        self.assertEqual(summary["fraction"], "0/0")
        self.assertIsNone(summary["current_topic"])


if __name__ == "__main__":
    unittest.main()
