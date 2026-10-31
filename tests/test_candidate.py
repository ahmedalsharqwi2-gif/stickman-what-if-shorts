import hashlib
from pathlib import Path
import pytest
from stickman.candidate import frame, render, scene_at

def test_timeline_ends_on_final_scene_without_looping():
    assert scene_at(0,120)==(0,0)
    assert scene_at(60,120)==(4,0)
    assert scene_at(119.99,120)[0]==7

def test_frames_move_within_scene_and_keep_vertical_format():
    first=frame(2,width=270,height=480)
    second=frame(3,width=270,height=480)
    assert first.size==(270,480)
    assert hashlib.sha256(first.tobytes()).digest()!=hashlib.sha256(second.tobytes()).digest()

def test_real_candidate_requires_narration(tmp_path):
    with pytest.raises(ValueError,match='narration'):
        render(tmp_path/'film.mp4')

def test_short_candidate_rejected(tmp_path):
    with pytest.raises(ValueError,match='120'):
        render(tmp_path/'film.mp4',duration=119,visual_review=True)

def test_existing_film_never_overwritten(tmp_path):
    film=tmp_path/'film.mp4';film.write_bytes(b'original evidence')
    with pytest.raises(FileExistsError):render(film,visual_review=True)
    assert film.read_bytes()==b'original evidence'

def test_arabic_font_shapes_and_scene_labels_fit_safe_area():
    from PIL import ImageFont, features
    from stickman.candidate import FONT,BEATS
    assert features.check('raqm'), 'Arabic shaping requires RAQM; do not render disconnected letters'
    font=ImageFont.truetype(str(FONT),31)
    assert max(font.getlength(beat[1],direction='rtl') for beat in BEATS)<810
