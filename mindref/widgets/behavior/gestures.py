from typing import Protocol, TypedDict

from kivy.gesture import Gesture, GestureDatabase

gdb = GestureDatabase()


class PointDict(TypedDict):
    points: list[tuple[float, float]]


class TouchUserData(Protocol):
    ud: PointDict


def make_gesture(data: list[dict]) -> Gesture:
    gesture_obj = Gesture()
    gesture_obj.add_stroke(point_list=data[0]["strokes"][0])
    gesture_obj.normalize()
    gesture_obj.name = data[0]["name"]
    return gesture_obj


def make_ud_gesture(touch: TouchUserData) -> Gesture:
    """Given list of points create a Gesture for matching database"""
    gesture_obj = Gesture()
    gesture_obj.add_stroke(point_list=touch.ud["points"])
    gesture_obj.normalize()
    return gesture_obj


swipe_right_data = gdb.str_to_gesture(
    "eNp1kEFqxSAQhvdzkmwadDQaLxB4F8i2CA2v0sRI9FF6+46alkj7XCTwzec4"
    "/3RrYNC9BQ6zt9sCAWGOny4sL4e7vycIAuIcDrcfLn1BkHDjjBHyjy3szqcIYSCmCMV07B/La1w8QQU3xgnSvcUnm9zuz4o"
    "+K9bfV7Ld5lZbm48wCdaz31YkG+i6NXAaceJSUW0S3NAvBc7BZjg2EAscWANFgcpUOFYoCxzP67pn16OyMWQDOXtuqGIo"
    "+dzQ2RASm6fHAkfdQJOh1MMVIstw4M3kWIIr1vTEElwJfg2OJbgy+gea65HZKFvQWHsh"
    "+8coW9BaVEPUxiW4NnVYlBXqCuuwqP5uAyk4fQ1E238Dt3eYDQ=="
)

swipe_left_data = gdb.str_to_gesture(
    "eNp1k0tugzAURedeCZNGfn7+sYFI2UCmFVJphUrAClRVd19zn9OEFBiAdHyxfY+h6pNW1VsidR6aS6uSUefpu0vtS9"
    "++zyqxms7p2o3Xbv5RyaoTaZ3R8HVJYzfMk0ouM5/RNF/Hz/Z1aocMvTppyjC/1w5zM3fjUEZCGWmGjz6nu0vXNzJ5VEfWB"
    "/03VQ7Xqqr6RHmHx2Apjx1N7fNjTkSqyZDjChqBWqAVyIDGCKRD/XjZJWGR0PJajPKaW6CPskAsC3hAxwK35gpIsJOE3kjEJeFiQCLkx"
    "+Pll0SNhOfdhNFIlE6bCfix9f4qBrKsc/sJmLOkn4dyXHwYmGOYvkOYYyfnFZxAmGO2KwhZrEuSBcKP8SI+aIFQYpwU9nJEDAumfAN"
    "+owHDgiGx4GVVRnEqJ+vlK2F0pcAriHrk9AqiHpUmN4h6ZJ5U0UMCXUnzfgLFy3dxY+gdy65EkEVtyL4z+R3Knsx/E1Z"
    "+Db0fgABfVieZFf29HI+Xk7Cof1NSGNrbsGK5b75HNTWHX9AU/ns="
)

swipe_left = make_gesture(swipe_left_data)
swipe_right = make_gesture(swipe_right_data)

gdb.add_gesture(swipe_left)
gdb.add_gesture(swipe_right)
