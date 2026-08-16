"""Integration tests for FastAPI endpoints using AAA (Arrange-Act-Assert) pattern."""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """
        Test that GET /activities returns all activities with correct structure.
        
        ARRANGE: Client is ready
        ACT: Send GET request to /activities
        ASSERT: Verify 200 status, 9 activities, and correct fields
        """
        # ACT
        response = client.get("/activities")

        # ASSERT
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) == 9
        
        # Verify structure of each activity
        for name, details in activities.items():
            assert isinstance(name, str)
            assert "description" in details
            assert "schedule" in details
            assert "max_participants" in details
            assert "participants" in details
            assert isinstance(details["participants"], list)


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_success(self, client, sample_activity, new_student_email):
        """
        Test successful student signup for an activity.
        
        ARRANGE: Prepare activity name and new student email
        ACT: Send POST signup request
        ASSERT: Verify 200 status, confirmation message, and participant added
        """
        # ARRANGE
        initial_response = client.get("/activities")
        initial_participants = initial_response.json()[sample_activity]["participants"]
        initial_count = len(initial_participants)

        # ACT
        response = client.post(
            f"/activities/{sample_activity}/signup",
            params={"email": new_student_email}
        )

        # ASSERT
        assert response.status_code == 200
        assert "message" in response.json()
        assert new_student_email in response.json()["message"]
        
        # Verify participant was added
        verify_response = client.get("/activities")
        updated_participants = verify_response.json()[sample_activity]["participants"]
        assert len(updated_participants) == initial_count + 1
        assert new_student_email in updated_participants

    def test_signup_invalid_activity_returns_404(self, client, new_student_email):
        """
        Test signup for non-existent activity returns 404.
        
        ARRANGE: Prepare invalid activity name and valid email
        ACT: Send POST signup request with invalid activity
        ASSERT: Verify 404 status and error message
        """
        # ARRANGE
        invalid_activity = "NonExistentActivity"

        # ACT
        response = client.post(
            f"/activities/{invalid_activity}/signup",
            params={"email": new_student_email}
        )

        # ASSERT
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_duplicate_student_returns_400(self, client, sample_activity):
        """
        Test signup with duplicate student returns 400.
        
        ARRANGE: Prepare activity and email of already registered student
        ACT: Send POST signup request for duplicate
        ASSERT: Verify 400 status and duplicate error message
        """
        # ARRANGE
        # Get existing participant from the activity
        activities = client.get("/activities").json()
        existing_student = activities[sample_activity]["participants"][0]

        # ACT
        response = client.post(
            f"/activities/{sample_activity}/signup",
            params={"email": existing_student}
        )

        # ASSERT
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_missing_email_returns_422(self, client, sample_activity):
        """
        Test signup without email parameter returns 422 (validation error).
        
        ARRANGE: Prepare activity but no email
        ACT: Send POST signup request without email
        ASSERT: Verify 422 status
        """
        # ACT
        response = client.post(f"/activities/{sample_activity}/signup")

        # ASSERT
        assert response.status_code == 422


class TestUnregisterEndpoint:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint."""

    def test_unregister_success(self, client, sample_activity):
        """
        Test successful student unregister from an activity.
        
        ARRANGE: Get existing participant
        ACT: Send DELETE unregister request
        ASSERT: Verify 200 status and participant removed
        """
        # ARRANGE
        initial_response = client.get("/activities")
        existing_student = initial_response.json()[sample_activity]["participants"][0]
        initial_count = len(initial_response.json()[sample_activity]["participants"])

        # ACT
        response = client.delete(
            f"/activities/{sample_activity}/unregister",
            params={"email": existing_student}
        )

        # ASSERT
        assert response.status_code == 200
        assert "message" in response.json()
        assert existing_student in response.json()["message"]
        
        # Verify participant was removed
        verify_response = client.get("/activities")
        updated_participants = verify_response.json()[sample_activity]["participants"]
        assert len(updated_participants) == initial_count - 1
        assert existing_student not in updated_participants

    def test_unregister_invalid_activity_returns_404(self, client, new_student_email):
        """
        Test unregister from non-existent activity returns 404.
        
        ARRANGE: Prepare invalid activity name
        ACT: Send DELETE unregister request with invalid activity
        ASSERT: Verify 404 status and error message
        """
        # ARRANGE
        invalid_activity = "NonExistentActivity"

        # ACT
        response = client.delete(
            f"/activities/{invalid_activity}/unregister",
            params={"email": new_student_email}
        )

        # ASSERT
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_non_member_returns_400(self, client, sample_activity, new_student_email):
        """
        Test unregister for student not signed up returns 400.
        
        ARRANGE: Prepare activity and email of non-registered student
        ACT: Send DELETE unregister request for non-member
        ASSERT: Verify 400 status and error message
        """
        # ACT
        response = client.delete(
            f"/activities/{sample_activity}/unregister",
            params={"email": new_student_email}
        )

        # ASSERT
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_unregister_missing_email_returns_422(self, client, sample_activity):
        """
        Test unregister without email parameter returns 422.
        
        ARRANGE: Prepare activity but no email
        ACT: Send DELETE unregister request without email
        ASSERT: Verify 422 status
        """
        # ACT
        response = client.delete(f"/activities/{sample_activity}/unregister")

        # ASSERT
        assert response.status_code == 422


class TestRootRedirect:
    """Tests for GET / endpoint."""

    def test_root_redirects_to_static_index(self, client):
        """
        Test that GET / redirects to /static/index.html.
        
        ARRANGE: Client is ready
        ACT: Send GET request to /
        ASSERT: Verify redirect status and location header
        """
        # ACT
        response = client.get("/", follow_redirects=False)

        # ASSERT
        assert response.status_code == 307  # Temporary redirect
        assert response.headers["location"] == "/static/index.html"
