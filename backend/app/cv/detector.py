"""
YOLO + ByteTrack based multi-object detection/tracking pipeline for match
video.

`ultralytics` and `supervision` are heavy, network-touching (model weight
download) dependencies, so they are imported LAZILY inside functions/methods
only. Importing this module — and therefore `app.main` or the mock-data
flow — must never require them to be installed or reachable.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterator, List, Optional

import numpy as np

# COCO class ids used by stock ultralytics checkpoints.
COCO_PERSON_CLASS_ID = 0
COCO_BALL_CLASS_ID = 32  # 'sports ball'

DEFAULT_MODEL_WEIGHTS = "yolov8n.pt"


@dataclass
class Detection:
    """A single tracked detection in one frame."""

    track_id: int
    class_name: str  # "person" | "ball"
    x1: float
    y1: float
    x2: float
    y2: float
    confidence: float

    @property
    def center(self) -> tuple[float, float]:
        return ((self.x1 + self.x2) / 2.0, (self.y1 + self.y2) / 2.0)

    @property
    def foot_point(self) -> tuple[float, float]:
        """Bottom-center of the box — the standard ground-contact point used
        for homography projection to pitch coordinates."""
        return ((self.x1 + self.x2) / 2.0, self.y2)


@dataclass
class FrameDetections:
    frame_index: int
    timestamp: float
    detections: List[Detection] = field(default_factory=list)
    # Raw BGR frame, populated by process_video() so downstream steps (team
    # color classification) can extract crops without re-decoding the video.
    # Not serialized/returned to API consumers — internal pipeline use only.
    frame_bgr: Optional[np.ndarray] = None


class PlayerBallDetector:
    """Wraps a YOLO model + ByteTrack tracker to produce stable track IDs for
    players and the ball across a video.

    Model and tracker are constructed lazily on first use (see `_ensure_model`
    / `_ensure_tracker`), so simply instantiating this class has no heavy
    import or network cost.
    """

    def __init__(
        self,
        weights_path: str = DEFAULT_MODEL_WEIGHTS,
        confidence_threshold: float = 0.25,
        person_class_id: int = COCO_PERSON_CLASS_ID,
        ball_class_id: int = COCO_BALL_CLASS_ID,
    ) -> None:
        self.weights_path = weights_path
        self.confidence_threshold = confidence_threshold
        self.person_class_id = person_class_id
        self.ball_class_id = ball_class_id
        self._model = None
        self._tracker = None

    def _ensure_model(self):
        if self._model is None:
            from ultralytics import YOLO  # lazy import

            self._model = YOLO(self.weights_path)
        return self._model

    def _ensure_tracker(self):
        if self._tracker is None:
            import supervision as sv  # lazy import

            self._tracker = sv.ByteTrack()
        return self._tracker

    def _class_name(self, class_id: int) -> Optional[str]:
        if class_id == self.person_class_id:
            return "person"
        if class_id == self.ball_class_id:
            return "ball"
        return None

    def process_video(
        self, video_path: str, stride: int = 1
    ) -> Iterator[FrameDetections]:
        """Run detection + tracking over a video file, yielding one
        FrameDetections per (sampled) frame in order.

        `stride` > 1 skips frames for speed (useful for long videos); the
        tracker still receives every processed frame in sequence so track IDs
        stay stable.
        """
        import cv2  # lazy import
        import supervision as sv  # lazy import

        model = self._ensure_model()
        tracker = self._ensure_tracker()

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise IOError(f"Could not open video: {video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
        frame_index = 0

        try:
            while True:
                ok, frame = cap.read()
                if not ok:
                    break

                if frame_index % stride != 0:
                    frame_index += 1
                    continue

                results = model(frame, verbose=False, conf=self.confidence_threshold)[0]
                detections = sv.Detections.from_ultralytics(results)
                detections = tracker.update_with_detections(detections)

                frame_dets: List[Detection] = []
                for i in range(len(detections)):
                    class_id = int(detections.class_id[i])
                    class_name = self._class_name(class_id)
                    if class_name is None:
                        continue
                    track_id = detections.tracker_id[i]
                    if track_id is None:
                        continue
                    x1, y1, x2, y2 = detections.xyxy[i]
                    conf = (
                        float(detections.confidence[i])
                        if detections.confidence is not None
                        else 0.0
                    )
                    frame_dets.append(
                        Detection(
                            track_id=int(track_id),
                            class_name=class_name,
                            x1=float(x1),
                            y1=float(y1),
                            x2=float(x2),
                            y2=float(y2),
                            confidence=conf,
                        )
                    )

                yield FrameDetections(
                    frame_index=frame_index,
                    timestamp=frame_index / fps,
                    detections=frame_dets,
                    frame_bgr=frame,
                )
                frame_index += 1
        finally:
            cap.release()

    def extract_crop(self, frame: np.ndarray, detection: Detection) -> np.ndarray:
        """Extract the pixel crop for a detection's bounding box from a raw
        video frame (BGR numpy array), for downstream team-color classification."""
        h, w = frame.shape[:2]
        x1 = max(0, int(detection.x1))
        y1 = max(0, int(detection.y1))
        x2 = min(w, int(detection.x2))
        y2 = min(h, int(detection.y2))
        if x2 <= x1 or y2 <= y1:
            return np.zeros((1, 1, 3), dtype=frame.dtype)
        return frame[y1:y2, x1:x2]
