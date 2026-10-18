"""以獨立期望驗證每一類焦點故障，避免全被 stale-source 擋住而誤算通過。"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import motion_checks as checks


def fixture():
    contracts = checks.normalize_contract({'segments': [
        {'id': 'first-item', 'start': 0, 'end': 3,
         'targets': [{'id': 'application', 'name': '申請單'}], 'required_active': ['application']},
        {'id': 'second-item', 'start': 3, 'end': 6,
         'targets': [{'id': 'receipt', 'name': '退款單'}], 'required_active': ['receipt']},
    ]})
    states = []
    for frame in range(60):
        second = frame / 10
        target, label = ('application', '申請單') if second < 3 else ('receipt', '退款單')
        # 三秒切換，兩側契約和 renderer 狀態各自建立；邊界不可取上一段。
        x = 80 + min(frame % 30, 15) * 2
        item = {'id': target, 'text': label, 'opacity': 1, 'label_opacity': 1,
                'x': x, 'y': 100, 'w': 240, 'h': 100,
                'projected_bounds': {'x': x, 'y': 100, 'w': 240, 'h': 100},
                'bounds': {'x': x, 'y': 100, 'w': 240, 'h': 100}}
        states.append({'frame': frame, 't': second, 'scene': target,
                       'active': [target], 'visible': [item]})
    return states, contracts


def issues(states, contracts):
    return checks.check_state_shape(states, 10, 60) + checks.check_focus(
        states, contracts, width=960, height=540, opacity_threshold=0.6,
        safe_area={'left': 20, 'top': 20, 'right': 940, 'bottom': 440}) + checks.check_labels(states, contracts)


class MotionContractTests(unittest.TestCase):
    def test_valid_and_adjacent_boundary(self):
        states, contracts = fixture()
        self.assertEqual([], issues(states, contracts))

    def test_enumeration_missing_second_item(self):
        states, contracts = fixture()
        for state in states[30:]:
            state['visible'] = []
        actual = issues(states, contracts)
        self.assertTrue(any(i['code'] == 'focus-not-visible' and i.get('target') == 'receipt' for i in actual))

    def test_focus_disappears_before_narration_ends(self):
        states, contracts = fixture()
        for state in states[25:30]:
            state['active'] = []
        self.assertTrue(any(i['code'] == 'focus-not-active' and i.get('t', 0) >= 2.5 for i in issues(states, contracts)))

    def test_wrong_target_is_not_accepted(self):
        states, contracts = fixture()
        states[14]['active'] = ['receipt']
        self.assertTrue(any(i['code'] in {'focus-not-active', 'wrong-focus'} and i.get('frame') == 14 for i in issues(states, contracts)))

    def test_wrong_extra_focus_with_correct_item_also_fails(self):
        states, contracts = fixture()
        states[14]['active'] = ['application', 'receipt']
        self.assertTrue(any(i['code'] == 'wrong-focus' and i.get('frame') == 14 for i in issues(states, contracts)))

    def test_name_disappears_during_morph(self):
        states, contracts = fixture()
        states[38]['visible'][0]['text'] = ''
        self.assertTrue(any(i['code'] in {'label-missing', 'moving-name-missing', 'label-empty'} and i.get('frame') == 38 for i in issues(states, contracts)))

    def test_projected_crop_even_when_clipped_box_is_inside(self):
        states, contracts = fixture()
        item = states[18]['visible'][0]
        item['projected_bounds']['x'] = -60
        item['bounds']['x'] = 20
        item['bounds']['w'] = 160
        self.assertTrue(any(i['code'] == 'cropped-focus' and i.get('frame') == 18 for i in issues(states, contracts)))

    def test_nearly_invisible_object_fails_visibility(self):
        states, contracts = fixture()
        states[10]['visible'][0]['opacity'] = 0.02
        self.assertTrue(any(i['code'] == 'focus-not-visible' and i.get('frame') == 10 for i in issues(states, contracts)))

    def test_projected_bounds_are_required(self):
        states, contracts = fixture()
        states[12]['visible'][0].pop('projected_bounds')
        self.assertTrue(any(i['code'] == 'projected-bounds-missing' and i.get('frame') == 12 for i in issues(states, contracts)))

    def test_stale_source_is_a_separate_failure(self):
        with tempfile.TemporaryDirectory(prefix='motion-fingerprint-') as temp:
            root = Path(temp)
            source = root / 'captions.srt'
            source.write_text('原字幕', encoding='utf-8')
            manifest = root / 'sources.json'
            manifest.write_text(json.dumps({'files': [{'role': 'captions', 'path': str(source),
                                                       'sha256': checks.sha256(source)}]}), encoding='utf-8')
            self.assertEqual([], checks.check_fingerprints(manifest))
            source.write_text('新字幕', encoding='utf-8')
            self.assertTrue(any(i['code'] == 'source-changed' for i in checks.check_fingerprints(manifest)))


if __name__ == '__main__':
    unittest.main()
