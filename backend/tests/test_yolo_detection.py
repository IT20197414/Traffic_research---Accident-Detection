from backend.app.services.video_analyzer import VideoAnalyzer


class TensorLike:
    def __init__(self, values):
        self._values = values

    def tolist(self):
        return self._values


class Boxes:
    xyxy = TensorLike([[10, 20, 100, 120], [1, 2, 3, 4]])
    cls = TensorLike([1, 0])
    conf = TensorLike([0.91, 0.99])


class Result:
    boxes = Boxes()
    names = {0: "car", 1: "accident"}


def test_parse_yolo_accident_result_only_returns_accident_boxes():
    parsed = VideoAnalyzer._parse_yolo_accident_result(Result())

    assert parsed == [(10, 20, 100, 120, 0.91)]

