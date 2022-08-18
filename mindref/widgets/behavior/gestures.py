from typing import Protocol, TypedDict

from kivy.gesture import Gesture, GestureDatabase

gdb = GestureDatabase()


class PointDict(TypedDict):
    points: list[tuple[float, float]]


class TouchUserData(Protocol):
    ud: PointDict


def make_gesture(data: dict) -> Gesture:
    gesture_obj = Gesture()
    gesture_obj.add_stroke(point_list=data["strokes"][0])
    gesture_obj.normalize()
    gesture_obj.name = data["name"]
    return gesture_obj


def make_ud_gesture(touch: TouchUserData) -> Gesture:
    """Given list of points create a Gesture for matching database"""
    gesture_obj = Gesture()
    gesture_obj.add_stroke(point_list=touch.ud["points"])
    gesture_obj.normalize()
    return gesture_obj


swipes_data = [
    {
        "name": "swipe-right",
        "priority": 100,
        "numpoints": 16,
        "stroke_sens": True,
        "orientation_sens": True,
        "angle_similarity": 130.0,
        "strokes": (
            [
                (416.0, 442.0),
                (417.0, 442.0),
                (426.0, 443.0),
                (435.9, 446.0),
                (467.0, 451.0),
                (511.0, 457.0),
                (536.0, 458.9),
                (583.0, 464.0),
                (607.0, 467.0),
                (659.0, 474.0),
                (680.0, 478.0),
                (715.0, 483.0),
                (735.0, 488.0),
                (766.0, 494.0),
                (778.0, 498.0),
                (799.0, 502.0),
            ],
        ),
    },
    {
        "name": "swipe-right",
        "priority": 100,
        "numpoints": 16,
        "stroke_sens": True,
        "orientation_sens": True,
        "angle_similarity": 130.0,
        "strokes": (
            [
                (440.0, 386.0),
                (442.0, 385.0),
                (446.0, 384.0),
                (460.0, 382.0),
                (472.0, 382.0),
                (497.0, 383.0),
                (514.0, 384.0),
                (547.0, 386.0),
                (569.0, 387.0),
                (604.0, 388.0),
                (629.0, 388.0),
                (662.0, 388.0),
                (703.0, 389.9),
                (720.0, 391.0),
                (750.0, 394.0),
                (764.0, 396.0),
                (785.0, 398.9),
                (793.0, 401.0),
                (799.0, 402.0),
            ],
        ),
    },
    {
        "name": "swipe-right",
        "priority": 100,
        "numpoints": 16,
        "stroke_sens": True,
        "orientation_sens": True,
        "angle_similarity": 130.0,
        "strokes": (
            [
                (423.0, 317.0),
                (424.0, 317.0),
                (428.9, 318.0),
                (447.0, 319.0),
                (456.0, 319.9),
                (482.0, 319.9),
                (500.0, 319.9),
                (534.0, 319.9),
                (550.0, 319.0),
                (585.0, 318.0),
                (604.0, 318.0),
                (650.0, 318.0),
                (667.0, 319.0),
                (699.0, 320.9),
                (720.0, 323.0),
                (734.0, 325.0),
                (754.0, 327.0),
                (759.0, 328.0),
                (767.0, 329.0),
                (768.0, 329.0),
            ],
        ),
    },
    {
        "name": "swipe-right",
        "priority": 100,
        "numpoints": 16,
        "stroke_sens": True,
        "orientation_sens": True,
        "angle_similarity": 130.0,
        "strokes": (
            [
                (456.0, 50.0),
                (456.9, 50.0),
                (459.0, 50.9),
                (462.0, 53.0),
                (467.0, 56.9),
                (482.0, 68.0),
                (513.0, 88.0),
                (526.0, 95.0),
                (568.0, 108.0),
                (600.0, 114.0),
                (666.0, 124.0),
                (694.0, 127.0),
                (748.0, 134.9),
                (773.0, 139.0),
                (799.0, 149.9),
            ],
        ),
    },
    {
        "name": "swipe-right",
        "priority": 100,
        "numpoints": 16,
        "stroke_sens": True,
        "orientation_sens": True,
        "angle_similarity": 130.0,
        "strokes": (
            [
                (252.0, 362.0),
                (252.9, 363.0),
                (268.0, 366.0),
                (282.0, 367.0),
                (323.0, 369.0),
                (379.0, 369.9),
                (413.0, 369.9),
                (481.0, 373.0),
                (511.0, 374.0),
                (576.0, 378.9),
                (603.0, 382.0),
                (651.0, 385.0),
                (666.0, 386.0),
                (702.0, 388.0),
            ],
        ),
    },
    {
        "name": "swipe-left",
        "priority": 100,
        "numpoints": 16,
        "stroke_sens": True,
        "orientation_sens": True,
        "angle_similarity": 130.0,
        "strokes": (
            [
                (559.0, 330.9),
                (551.0, 329.0),
                (542.0, 329.0),
                (527.0, 329.0),
                (498.0, 329.0),
                (480.0, 329.0),
                (444.0, 329.0),
                (421.0, 329.9),
                (368.0, 330.9),
                (340.0, 330.9),
                (281.0, 332.0),
                (245.0, 333.0),
                (171.0, 338.0),
                (135.0, 339.9),
                (75.0, 339.9),
            ],
        ),
    },
    {
        "name": "swipe-left",
        "priority": 100,
        "numpoints": 16,
        "stroke_sens": True,
        "orientation_sens": True,
        "angle_similarity": 130.0,
        "strokes": (
            [
                (672.0, 182.0),
                (666.0, 186.0),
                (646.0, 193.0),
                (633.0, 198.0),
                (601.0, 207.0),
                (582.0, 212.0),
                (540.0, 220.0),
                (505.9, 225.0),
                (397.0, 241.0),
                (332.0, 251.0),
                (205.0, 270.0),
                (156.0, 274.0),
                (108.0, 277.0),
                (104.0, 277.0),
            ],
        ),
    },
    {
        "name": "swipe-left",
        "priority": 100,
        "numpoints": 16,
        "stroke_sens": True,
        "orientation_sens": True,
        "angle_similarity": 130.0,
        "strokes": (
            [
                (614.0, 239.0),
                (613.0, 237.9),
                (595.0, 232.0),
                (558.0, 226.0),
                (532.0, 224.0),
                (473.0, 221.0),
                (441.0, 216.0),
                (382.0, 206.0),
                (348.0, 200.0),
                (296.0, 188.0),
                (270.0, 183.0),
                (223.0, 173.9),
                (193.0, 167.0),
            ],
        ),
    },
    {
        "name": "swipe-left",
        "priority": 100,
        "numpoints": 16,
        "stroke_sens": True,
        "orientation_sens": True,
        "angle_similarity": 130.0,
        "strokes": (
            [
                (412.0, 280.9),
                (409.0, 283.0),
                (400.0, 288.0),
                (387.0, 296.0),
                (356.0, 312.0),
                (336.0, 319.9),
                (293.0, 335.0),
                (270.0, 339.9),
                (209.0, 350.9),
                (176.0, 357.0),
                (108.0, 367.0),
                (79.0, 371.0),
                (53.0, 375.0),
            ],
        ),
    },
    {
        "name": "swipe-left",
        "priority": 100,
        "numpoints": 16,
        "stroke_sens": True,
        "orientation_sens": True,
        "angle_similarity": 130.0,
        "strokes": (
            [
                (215.0, 432.0),
                (213.0, 432.0),
                (201.0, 432.0),
                (188.0, 433.0),
                (160.0, 436.0),
                (144.0, 437.0),
                (114.0, 437.0),
            ],
        ),
    },
]

swipe_lefts = (
    make_gesture(stroke) for stroke in swipes_data if stroke["name"] == "swipe-left"
)
swipe_rights = (
    make_gesture(stroke) for stroke in swipes_data if stroke["name"] == "swipe-right"
)

for gesture_pipe in (swipe_lefts, swipe_rights):
    for gesture in gesture_pipe:
        gdb.add_gesture(gesture)
