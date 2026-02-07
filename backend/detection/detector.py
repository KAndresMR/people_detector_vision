from .hog_opencv import HogOpenCVDetector

class PersonDetector:
    def __init__(self, mode="opencv"):
        if mode == "opencv":
            self.detector = HogOpenCVDetector()
        else:
            raise ValueError("Detector no soportado")

    def detect(self, image):
        """
        Devuelve lista de detecciones en formato:
        [{"bbox": (x, y, w, h), "confidence": 0.8}, ...]
        """
        raw_detections = self.detector.detect(image)
        detections = []

        for det in raw_detections:
            # Si HogOpenCVDetector devuelve objetos con bbox y confidence
            if hasattr(det, "bbox") and hasattr(det, "confidence"):
                detections.append({
                    "bbox": det.bbox,
                    "confidence": det.confidence
                })
            else:
                # Si devuelve tuplas (x, y, w, h, conf)
                detections.append({
                    "bbox": det[:4],
                    "confidence": det[4] if len(det) > 4 else 1.0
                })
        return detections
