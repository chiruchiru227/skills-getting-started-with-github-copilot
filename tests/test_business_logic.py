"""Unit tests for core business logic using AAA (Arrange-Act-Assert) pattern."""

import pytest
from fastapi import HTTPException
from src.app import signup_for_activity, unregister_from_activity, activities


class TestSignupLogic:
    """Tests for signup_for_activity business logic."""

    def test_signup_adds_participant_to_activity(self):
        """
        Test that signup successfully adds a participant.
        
        ARRANGE: Prepare test data with fresh activities dict
        ACT: Call signup_for_activity
        ASSERT: Verify participant added to activity
        """
        # ARRANGE
        test_email = "logic_test@mergington.edu"
        activity_name = "Chess Club"
        initial_count = len(activities[activity_name]["participants"])

        # ACT
        result = signup_for_activity(activity_name, test_email)

        # ASSERT
        assert test_email in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count + 1
        assert "Signed up" in result["message"]
        
        # CLEANUP: Remove test participant
        activities[activity_name]["participants"].remove(test_email)

    def test_signup_duplicate_raises_400_exception(self):
        """
        Test that signing up duplicate student raises HTTPException 400.
        
        ARRANGE: Prepare activity and existing participant
        ACT: Try to signup the same student twice
        ASSERT: Second attempt raises HTTPException(400)
        """
        # ARRANGE
        activity_name = "Programming Class"
        existing_student = activities[activity_name]["participants"][0]

        # ACT & ASSERT
        with pytest.raises(HTTPException) as exc_info:
            signup_for_activity(activity_name, existing_student)
        
        assert exc_info.value.status_code == 400
        assert "already signed up" in exc_info.value.detail

    def test_signup_invalid_activity_raises_404_exception(self):
        """
        Test that signup for invalid activity raises HTTPException 404.
        
        ARRANGE: Prepare invalid activity name
        ACT: Try to signup for non-existent activity
        ASSERT: Raises HTTPException(404)
        """
        # ARRANGE
        invalid_activity = "FakeActivityThatDoesNotExist"
        test_email = "student@mergington.edu"

        # ACT & ASSERT
        with pytest.raises(HTTPException) as exc_info:
            signup_for_activity(invalid_activity, test_email)
        
        assert exc_info.value.status_code == 404
        assert "Activity not found" in exc_info.value.detail


class TestUnregisterLogic:
    """Tests for unregister_from_activity business logic."""

    def test_unregister_removes_participant_from_activity(self):
        """
        Test that unregister successfully removes a participant.
        
        ARRANGE: Add a test participant, then prepare for unregister
        ACT: Call unregister_from_activity
        ASSERT: Verify participant removed from activity
        """
        # ARRANGE
        test_email = "unregister_test@mergington.edu"
        activity_name = "Gym Class"
        
        # Add test participant first
        activities[activity_name]["participants"].append(test_email)
        initial_count = len(activities[activity_name]["participants"])

        # ACT
        result = unregister_from_activity(activity_name, test_email)

        # ASSERT
        assert test_email not in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count - 1
        assert "Unregistered" in result["message"]

    def test_unregister_non_member_raises_400_exception(self):
        """
        Test that unregistering non-member raises HTTPException 400.
        
        ARRANGE: Prepare activity and non-registered email
        ACT: Try to unregister student not in activity
        ASSERT: Raises HTTPException(400)
        """
        # ARRANGE
        activity_name = "Music Band"
        non_member_email = "nonmember@mergington.edu"

        # ACT & ASSERT
        with pytest.raises(HTTPException) as exc_info:
            unregister_from_activity(activity_name, non_member_email)
        
        assert exc_info.value.status_code == 400
        assert "not signed up" in exc_info.value.detail

    def test_unregister_invalid_activity_raises_404_exception(self):
        """
        Test that unregister from invalid activity raises HTTPException 404.
        
        ARRANGE: Prepare invalid activity name
        ACT: Try to unregister from non-existent activity
        ASSERT: Raises HTTPException(404)
        """
        # ARRANGE
        invalid_activity = "FakeActivityThatDoesNotExist"
        test_email = "student@mergington.edu"

        # ACT & ASSERT
        with pytest.raises(HTTPException) as exc_info:
            unregister_from_activity(invalid_activity, test_email)
        
        assert exc_info.value.status_code == 404
        assert "Activity not found" in exc_info.value.detail
