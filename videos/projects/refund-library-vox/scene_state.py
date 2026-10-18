#!/usr/bin/env python3
"""B 候選（y2_vox 改編）的單一幾何來源：輸出逐幀 state.json，renderer 只依此繪製。

桌面世界座標固定；鏡頭依當下要讀的物件反算落點。鏡頭逐幀平滑，
桌上元素（描線、圈、螢光、蓋章、撕下）依 y2_vox「一拍二」以 12fps 步進。
active 只代表畫面實際的焦點表現；旁白期望另見 materials/focus.json。
移動中的紙件名稱必須已印在紙上：申請單不移動，以蓋章表示送出；
退款單是原訂單下緣的撕線聯，先寫上名稱，再沿空白桌面撕下。
"""
from __future__ import annotations

import json
import math
from pathlib import Path

FPS = 30
FRAMES = 733                      # 24.433 秒 × 30fps，與 prepare 的 timeline 相同
SAFE = (48, 32, 1232, 570)        # 與 profile content_safe_area 相同
VIEW_W, VIEW_H = SAFE[2] - SAFE[0], SAFE[3] - SAFE[1]
VIEW_CX, VIEW_CY = (SAFE[0] + SAFE[2]) / 2, (SAFE[1] + SAFE[3]) / 2

# ---- 桌面上的紙件（世界座標 x, y, w, h）----
ITEMS = {
    "order-doc":        {"text": "原訂單",   "kind": "doc",    "rect": (160, 120, 600, 480), "rot": 0.0},
    "product-row":      {"text": "商品",     "kind": "row",    "rect": (190, 292, 540, 78), "parent": "order-doc"},
    "reason-row":       {"text": "退款原因", "kind": "row",    "rect": (190, 388, 540, 78), "parent": "order-doc"},
    "application-slip": {"text": "退款申請", "kind": "slip",   "rect": (800, 150, 310, 200), "rot": -2.0},
    "reviewer-card":    {"text": "審核人",   "kind": "badge",  "rect": (1210, 150, 300, 380), "rot": 1.5},
    "conditions-card":  {"text": "退款條件", "kind": "conditions", "rect": (1590, 150, 420, 430), "rot": -1.0},
    "approval-stamp":   {"text": "通過",     "kind": "stamp",  "rect": (1780, 470, 200, 92), "rot": -8.0},
    "refund-slip":      {"text": "退款單",   "kind": "refund", "rect": (160, 600, 600, 120), "rot": 0.0},
    "payment-link":     {"text": "回接",     "kind": "link",   "rect": (760, 790, 100, 90)},
    "payment-ledger":   {"text": "付款紀錄", "kind": "ledger", "rect": (860, 640, 660, 410), "rot": 0.6},
    "amount-row":       {"text": "金額",     "kind": "row",    "rect": (890, 736, 600, 76), "parent": "payment-ledger"},
    "method-row":       {"text": "方式",     "kind": "row",    "rect": (890, 828, 600, 76), "parent": "payment-ledger"},
    "progress-row":     {"text": "進度",     "kind": "row",    "rect": (890, 920, 600, 76), "parent": "payment-ledger"},
    "trace-label":      {"text": "追蹤每一筆款項", "kind": "label", "rect": (1066, 1012, 430, 92), "rot": -1.2},
}
REFUND_FINAL = (200, 770, 560, 120, -2.0)   # 撕下後的位置：原訂單正下方的空白桌面

# 紅線（世界座標，三次貝茲：起點、控制點、控制點、終點）
STRINGS = {
    "handoff": ((1110, 250), (1150, 300), (1170, 300), (1210, 262)),
    "check":   ((1510, 300), (1540, 330), (1560, 330), (1590, 300)),
    "link":    ((760, 846), (792, 876), (828, 876), (860, 846)),
}
LINK_LABEL = (774, 794, 72, 40)    # 「回接」字樣：退款單與帳本之間的空白，不壓任何文字


def clamp(v, lo=0.0, hi=1.0):
    return max(lo, min(hi, v))


def step12(t):
    return math.floor(t * 12 + 1e-6) / 12


def prog(t, start, end, stepped=True):
    tt = step12(t) if stepped else t
    if t >= end:          # 到達結束時間必定完成，不因 12fps 量化殘留未完成
        return 1.0
    return clamp((tt - start) / (end - start))


def sine_in_out(p):
    return -(math.cos(math.pi * p) - 1) / 2


def bezier_ease(p, x1=0.33, y1=0.0, x2=0.2, y2=1.0):
    """長尾緩動 cubic-bezier(.33,0,.2,1)。"""
    if p <= 0 or p >= 1:
        return clamp(p)
    lo, hi = 0.0, 1.0
    for _ in range(40):
        mid = (lo + hi) / 2
        x = 3 * (1 - mid) ** 2 * mid * x1 + 3 * (1 - mid) * mid ** 2 * x2 + mid ** 3
        lo, hi = (mid, hi) if x < p else (lo, mid)
    u = (lo + hi) / 2
    return 3 * (1 - u) ** 2 * u * y1 + 3 * (1 - u) * u ** 2 * y2 + u ** 3


def frame_box(x0, y0, x1, y1, margin):
    w, h = x1 - x0 + 2 * margin, y1 - y0 + 2 * margin
    s = min(VIEW_W / w, VIEW_H / h)
    return ((x0 + x1) / 2, (y0 + y1) / 2, s)


# ---- 鏡頭：依當下要讀的物件反算落點 ----
CAM_WIDE = frame_box(100, 80, 1560, 760, 0)
CAM_ORDER = frame_box(160, 120, 760, 720, 30)
CAM_ROWS = frame_box(190, 150, 1110, 470, 40)        # 兩列＋右側申請單；送出時不需移鏡
CAM_HANDOFF = frame_box(800, 150, 2010, 580, 40)   # 交棒時已帶入右側條件卡，之後只做小幅推近
CAM_COND = frame_box(1210, 150, 2010, 580, 46)
CAM_CONVERT = frame_box(160, 120, 760, 890, 34)      # 原訂單與撕下後的退款單
CAM_LINK = frame_box(200, 640, 1520, 1050, 30)       # 退款單與付款紀錄
CAM_LEDGER_ROWS = frame_box(890, 736, 1496, 1104, 50)   # 三列＋帳本下緣的追蹤標籤位置
CAM_ALL = frame_box(160, 120, 2020, 1104, 30)

# (開始, 結束, 起點, 終點, 緩動)；區間外保持；12.72 為句讀硬切。
CAMERA = [
    (0.0, 0.25, CAM_WIDE, CAM_WIDE, None),
    (0.25, 1.45, CAM_WIDE, CAM_ORDER, sine_in_out),
    (2.24, 2.80, CAM_ORDER, CAM_ROWS, sine_in_out),
    (7.20, 8.30, CAM_ROWS, CAM_HANDOFF, bezier_ease),
    (9.48, 10.38, CAM_HANDOFF, CAM_COND, sine_in_out),
    (12.72, 12.72, CAM_CONVERT, CAM_CONVERT, None),      # 硬切：「通過後，」句讀停頓之後
    (16.34, 17.20, CAM_CONVERT, CAM_LINK, sine_in_out),
    (19.04, 19.58, CAM_LINK, CAM_LEDGER_ROWS, sine_in_out),
    (22.44, 23.29, CAM_LEDGER_ROWS, CAM_ALL, bezier_ease),
]


def lerp(a, b, p):
    return a + (b - a) * p


def camera_at(t):
    current = CAMERA[0][2]
    for start, end, a, b, ease in CAMERA:
        if t < start:
            break
        if end <= start or t >= end:
            current = b
        else:
            p = ease((t - start) / (end - start)) if ease else 1.0
            s = math.exp(lerp(math.log(a[2]), math.log(b[2]), p))   # 縮放以對數內插
            current = (lerp(a[0], b[0], p), lerp(a[1], b[1], p), s)
    return current


def project(cam, x, y):
    cx, cy, s = cam
    return ((x - cx) * s + VIEW_CX, (y - cy) * s + VIEW_CY)


def rotated_bbox(rect, rot):
    x, y, w, h = rect
    cx, cy = x + w / 2, y + h / 2
    r = math.radians(rot)
    pts = [(cx + dx * math.cos(r) - dy * math.sin(r), cy + dx * math.sin(r) + dy * math.cos(r))
           for dx, dy in ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2))]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)


# ---- 畫面實際焦點節拍（旁白期望另見 focus.json）----
BEATS = [
    (0.0, "order-doc"), (2.24, "product-row"), (3.74, "reason-row"), (4.98, "application-slip"),
    (8.48, "reviewer-card"), (9.48, "conditions-card"), (11.7, "approval-stamp"), (12.72, "order-doc"),
    (13.88, "refund-slip"), (17.34, "payment-link"), (17.86, "payment-ledger"), (19.04, "amount-row"),
    (20.2, "method-row"), (21.06, "progress-row"), (22.44, "trace-label"),
]


def active_at(t):
    current = BEATS[0][1]
    for start, item in BEATS:
        if t + 1e-9 >= start:
            current = item
    return current


# ---- 標記：揭示動作輪換（底線、手畫圈、螢光、蓋章、紅線、打勾、撕線）----
def marks_at(t):
    return [
        {"id": "ul-order", "kind": "underline", "owner": "order-doc", "rect": (178, 196, 210, 14), "p": prog(t, 1.52, 2.0)},
        {"id": "circle-product", "kind": "circle", "owner": "product-row", "rect": (186, 284, 214, 94), "p": prog(t, 2.62, 3.18)},
        {"id": "hl-reason", "kind": "highlight", "owner": "reason-row", "rect": (200, 404, 172, 48), "p": prog(t, 3.74, 4.40)},
        {"id": "stamp-sent", "kind": "stamp", "owner": "application-slip", "rect": (930, 270, 150, 58), "rot": -9, "text": "已送出", "p": prog(t, 4.98, 5.24)},
        {"id": "str-handoff", "kind": "string", "owner": "application-slip", "pts": STRINGS["handoff"], "p": prog(t, 7.30, 8.30)},
        {"id": "circle-reviewer", "kind": "circle", "owner": "reviewer-card", "rect": (1228, 418, 264, 98), "p": prog(t, 8.48, 9.04)},
        {"id": "str-check", "kind": "string", "owner": "conditions-card", "pts": STRINGS["check"], "p": prog(t, 9.48, 9.90)},
        {"id": "check-1", "kind": "check", "owner": "conditions-card", "rect": (1620, 262, 40, 40), "p": prog(t, 10.16, 10.36)},
        {"id": "check-2", "kind": "check", "owner": "conditions-card", "rect": (1620, 342, 40, 40), "p": prog(t, 10.50, 10.70)},
        {"id": "check-3", "kind": "check", "owner": "conditions-card", "rect": (1620, 422, 40, 40), "p": prog(t, 10.84, 11.04)},
        {"id": "circle-order", "kind": "circle", "owner": "order-doc", "rect": (147, 119, 240, 116), "p": prog(t, 12.72, 13.10)},   # 圈住整個標籤，線不經過標籤文字
        {"id": "perf", "kind": "perforation", "owner": "refund-slip", "rect": (160, 600, 600, 0), "p": prog(t, 13.14, 13.40)},
        {"id": "str-link", "kind": "string", "owner": "payment-link", "pts": STRINGS["link"], "p": prog(t, 17.34, 17.74)},
        {"id": "ul-ledger", "kind": "underline", "owner": "payment-ledger", "rect": (880, 712, 220, 14), "p": prog(t, 17.86, 18.30)},
        {"id": "hl-amount", "kind": "highlight", "owner": "amount-row", "rect": (900, 750, 134, 48), "p": prog(t, 19.58, 20.02)},
        {"id": "ul-method", "kind": "underline", "owner": "method-row", "rect": (904, 884, 112, 12), "p": prog(t, 20.20, 20.60)},
        {"id": "circle-progress", "kind": "circle", "owner": "progress-row", "rect": (884, 914, 168, 88), "p": prog(t, 21.06, 21.60)},
        {"id": "ul-trace", "kind": "underline", "owner": "trace-label", "rect": (1090, 1090, 380, 12), "p": prog(t, 22.90, 23.40)},
    ]


def refund_state(t):
    """撕線聯：12.72 前是原訂單下緣的空白聯；13.14–13.40 寫上名稱並畫撕線；13.40–13.85 撕下。"""
    typed = "退款單"[: round(3 * prog(t, 13.14, 13.40))] if t >= 13.14 else ""
    p = prog(t, 13.40, 13.85)
    e = 1 - (1 - p) ** 4
    x0, y0, w0, h0, rot0 = 160, 600, 600, 120, 0.0
    x1, y1, w1, h1, rot1 = REFUND_FINAL
    rect = (lerp(x0, x1, e), lerp(y0, y1, e), lerp(w0, w1, e), lerp(h0, h1, e))
    lift = math.sin(math.pi * e) * 4.0          # 撕下途中略微翹起
    return rect, lerp(rot0, rot1, e) + lift, typed, ("attached" if p <= 0 else "detached")


def item_motion(item_id, t):
    """回傳 (rect, rot, opacity, z, text, extra)。"""
    spec = ITEMS[item_id]
    rect = spec["rect"]
    rot = spec.get("rot", 0.0)
    opacity, z, text, extra = 1.0, 10, spec["text"], {}
    if item_id == "refund-slip":
        rect, rot, text, mode = refund_state(t)
        extra = {"mode": mode}
        z = 11 if mode == "attached" else 30   # 未撕下時壓住訂單下緣陰影，與訂單接成同一張紙
    elif item_id == "approval-stamp":
        if t < 11.70:
            opacity = 0.0
        p = prog(t, 11.70, 11.94)
        scale = lerp(1.45, 1.0, p)
        x, y, w, h = rect
        cx, cy = x + w / 2, y + h / 2
        rect = (cx - w * scale / 2, cy - h * scale / 2, w * scale, h * scale)
        z = 40
    elif item_id == "payment-link":
        if t < 17.34:
            opacity = 0.0
        z = 35
    elif item_id == "trace-label":
        if t < 22.44:
            opacity = 0.0
        z = 60
    elif spec["kind"] == "row":
        z = 15
    elif item_id == "payment-ledger":
        z = 8
    return rect, rot, opacity, z, text, extra


def build():
    frames = []
    for f in range(FRAMES):
        t = round(f / FPS, 6)
        cam = camera_at(t)
        visible = []
        for item_id, spec in ITEMS.items():
            rect, rot, opacity, z, text, extra = item_motion(item_id, t)
            if opacity <= 0:
                continue
            bx, by, bw, bh = rotated_bbox(rect, rot)
            x0, y0 = project(cam, bx, by)
            x1, y1 = project(cam, bx + bw, by + bh)
            pb = {"x": round(x0, 2), "y": round(y0, 2), "w": round(x1 - x0, 2), "h": round(y1 - y0, 2)}
            visible.append({
                "id": item_id, "text": text, "kind": spec["kind"], "opacity": opacity,
                "world": {"x": round(rect[0], 3), "y": round(rect[1], 3), "w": round(rect[2], 3), "h": round(rect[3], 3)},
                "rot": round(rot, 3), "z": z, "parent": spec.get("parent"), **extra,
                "projected_bounds": pb, **pb,
            })
        frames.append({
            "frame": f, "t": t,
            "scene": "order-apply" if t < 7.2 else "review-handoff" if t < 15.567 else "payment-track",
            "active": [active_at(t)],
            "camera": {"cx": round(cam[0], 4), "cy": round(cam[1], 4), "s": round(cam[2], 6)},
            "visible": visible,
            "marks": [{**m, "p": round(m["p"], 4)} for m in marks_at(t)],
        })
    return {"fps": FPS, "width": 1280, "height": 720, "safe": SAFE, "view": [VIEW_CX, VIEW_CY],
            "desk": {"w": 2200, "h": 1200}, "link_label": LINK_LABEL, "frames": frames}


if __name__ == "__main__":
    out = Path(__file__).with_name("materials") / "state.json"
    out.write_text(json.dumps(build(), ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(out)
