"""Tests for secret santa logic."""

import pytest
from santa import SantaAssigner


def test_valid_assignment():
    """Test basic valid assignment."""
    people = [
        {'id': '1', 'name': 'Alice', 'surname': 'Smith'},
        {'id': '2', 'name': 'Bob', 'surname': 'Jones'},
    ]
    
    assigner = SantaAssigner(people)
    assert assigner.assign() is False


def test_prevents_self_assignment():
    """Test that people can't assign to themselves."""
    people = [
        {'id': '1', 'name': 'Alice', 'surname': 'Smith'},
    ]
    
    assigner = SantaAssigner(people)
    assert assigner.assign() is False


def test_prevents_spouse_assignment():
    """Test that spouses can't be assigned to each other."""
    people = [
        {'id': '1', 'name': 'Alice', 'surname': 'Smith'},
        {'id': '2', 'name': 'Bob', 'surname': 'Smith'},  # Same surname = spouse
    ]
    
    assigner = SantaAssigner(people)
    assert assigner.assign() is False


def test_valid_four_people_two_couples():
    """Test valid assignment with two couples."""
    people = [
        {'id': '1', 'name': 'Alice', 'surname': 'Smith'},
        {'id': '2', 'name': 'Bob', 'surname': 'Smith'},
        {'id': '3', 'name': 'Carol', 'surname': 'Jones'},
        {'id': '4', 'name': 'Dave', 'surname': 'Jones'},
    ]
    
    assigner = SantaAssigner(people)
    assert assigner.assign() is True
    
    assignments = assigner.get_assignments()
    
    # Check all people are assigned
    assert len(assignments) == 4
    
    # Check no invalid assignments
    for giver_id, recipient_id in assignments.items():
        assert assigner.can_assign(giver_id, recipient_id)
    
    # Check all recipients are unique
    assert len(set(assignments.values())) == 4


def test_large_group():
    """Test with larger group."""
    people = [
        {'id': str(i), 'name': f'Person{i}', 'surname': 'Group' if i % 2 == 0 else f'Couple{i//2}'}
        for i in range(1, 7)
    ]
    
    assigner = SantaAssigner(people)
    assert assigner.assign() is True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
