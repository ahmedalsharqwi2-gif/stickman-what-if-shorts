"""Check visible cause and contact, rather than just changing captions."""
import math

import pytest

from stickman.story_actions import STORIES, solve_joint, state_at


def distance(a, b):
    return math.dist(a, b)


def test_arm_preserves_lengths_and_reaches_target():
    elbow, hand = solve_joint((0, 0), (160, 60), 110, 115)
    assert distance((0, 0), elbow) == pytest.approx(110)
    assert distance(elbow, hand) == pytest.approx(115)
    assert distance(hand, (160, 60)) < 0.001


def test_miss_then_actual_phone_contact():
    missed = state_at('orbital_phone', 7.9)
    caught = state_at('orbital_phone', 27.9)
    assert distance(missed['hands'][1], missed['phone']) > 80
    assert caught['held']
    assert distance(caught['hands'][1], caught['phone']) < 0.001


def test_air_running_moves_legs_without_chasing_phone():
    start = state_at('orbital_phone', 12.1)
    later = state_at('orbital_phone', 12.7)
    assert distance(start['hip'], later['hip']) < 5
    assert distance(start['feet'][0], later['feet'][0]) > 50


@pytest.mark.parametrize('scenario', STORIES)
def test_rope_pull_has_hand_contact_and_payoff(scenario):
    pulling = state_at(scenario, 22)
    assert distance(pulling['rope'][1], pulling['hands'][0]) < 0.001
    assert not pulling['goal_achieved']
    assert state_at(scenario, 31.8)['goal_achieved']
    assert len({beat[0] for beat in STORIES[scenario]['beats']}) >= 6


def test_luggage_catch_reaches_handle():
    caught = state_at('slippery_luggage', 27.99)
    handle = (caught['bag'][0], caught['bag'][1] - 105)
    assert caught['held']
    assert distance(caught['hands'][1], handle) < 12


def test_stories_use_distinct_worlds_and_actions():
    assert STORIES['orbital_phone']['world'] != STORIES['slippery_luggage']['world']
    assert not ({b[1] for b in STORIES['orbital_phone']['beats']} &
                {b[1] for b in STORIES['slippery_luggage']['beats']})
