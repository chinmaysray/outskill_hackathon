import io
import json
import asyncio
from typing import Dict, Any, List, Tuple
from PIL import Image, ImageEnhance
import cv2
import numpy as np
import torch
from transformers import CLIPProcessor, CLIPModel, BlipProcessor, BlipForConditionalGeneration
from colorthief import ColorThief
import structlog

from app.core.config import settings
from app.schemas.analysis import ImageFeatures

logger = structlog.get_logger(__name__)

class ImageProcessor:
    """Advanced image processing with CLIP embeddings and computer vision analysis."""

    def __init__(self):
        self.clip_model = None
        self.clip_processor = None
        self.blip_model = None
        self.blip_processor = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.initialized = False

    async def initialize(self):
        """Initialize AI models asynchronously."""
        try:
            logger.info("Initializing image processing models", device=self.device)

            # Initialize CLIP model for embeddings
            self.clip_model = CLIPModel.from_pretrained(settings.clip_model_name)
            self.clip_processor = CLIPProcessor.from_pretrained(settings.clip_model_name)

            # Initialize BLIP for image captioning
            self.blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
            self.blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

            # Move models to device
            self.clip_model.to(self.device)
            self.blip_model.to(self.device)

            self.initialized = True
            logger.info("Image processing models initialized successfully")

        except Exception as e:
            logger.error("Failed to initialize image processing models", error=str(e))
            raise

    def is_healthy(self) -> bool:
        """Check if the image processor is healthy."""
        return self.initialized and self.clip_model is not None

    async def cleanup(self):
        """Cleanup resources."""
        logger.info("Cleaning up image processor")
        if self.clip_model:
            del self.clip_model
        if self.blip_model:
            del self.blip_model
        torch.cuda.empty_cache() if torch.cuda.is_available() else None

    async def process_image(self, image_bytes: bytes) -> ImageFeatures:
        """
        Comprehensive image processing pipeline.

        Args:
            image_bytes: Raw image data

        Returns:
            ImageFeatures: Extracted features and analysis
        """
        try:
            # Load and validate image
            image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            image_array = np.array(image)

            # Run processing pipeline in parallel
            tasks = [
                self._get_clip_embeddings(image),
                self._generate_description(image),
                self._extract_colors(image_bytes),
                self._analyze_layout(image_array),
                self._extract_text_elements(image_array),
                self._detect_ui_components(image_array)
            ]

            results = await asyncio.gather(*tasks)

            return ImageFeatures(
                clip_embeddings=results[0],
                description=results[1],
                color_palette=results[2],
                layout_analysis=results[3],
                text_elements=results[4],
                ui_components=results[5],
                dimensions={"width": image.width, "height": image.height},
                file_size=len(image_bytes)
            )

        except Exception as e:
            logger.error("Image processing failed", error=str(e))
            raise

    async def _get_clip_embeddings(self, image: Image.Image) -> List[float]:
        """Generate CLIP embeddings for semantic understanding."""
        try:
            inputs = self.clip_processor(images=image, return_tensors="pt").to(self.device)

            with torch.no_grad():
                image_features = self.clip_model.get_image_features(**inputs)
                # Normalize embeddings
                embeddings = image_features / image_features.norm(dim=-1, keepdim=True)

            return embeddings.cpu().numpy().flatten().tolist()

        except Exception as e:
            logger.error("CLIP embedding generation failed", error=str(e))
            return []

    async def _generate_description(self, image: Image.Image) -> str:
        """Generate natural language description using BLIP."""
        try:
            inputs = self.blip_processor(image, return_tensors="pt").to(self.device)

            with torch.no_grad():
                output = self.blip_model.generate(**inputs, max_length=50, num_beams=5)
                description = self.blip_processor.decode(output[0], skip_special_tokens=True)

            return description

        except Exception as e:
            logger.error("Image description generation failed", error=str(e))
            return "Description unavailable"

    async def _extract_colors(self, image_bytes: bytes) -> List[Dict[str, Any]]:
        """Extract dominant colors and color palette analysis."""
        try:
            color_thief = ColorThief(io.BytesIO(image_bytes))

            # Get dominant color
            dominant_color = color_thief.get_color(quality=1)

            # Get color palette
            palette = color_thief.get_palette(color_count=8, quality=1)

            colors = [{
                "rgb": list(dominant_color),
                "hex": "#{:02x}{:02x}{:02x}".format(*dominant_color),
                "role": "dominant"
            }]

            for i, color in enumerate(palette[1:], 1):  # Skip dominant color
                colors.append({
                    "rgb": list(color),
                    "hex": "#{:02x}{:02x}{:02x}".format(*color),
                    "role": f"palette_{i}"
                })

            return colors

        except Exception as e:
            logger.error("Color extraction failed", error=str(e))
            return []

    async def _analyze_layout(self, image_array: np.ndarray) -> Dict[str, Any]:
        """Analyze layout composition and visual structure."""
        try:
            # Convert to grayscale for analysis
            gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)

            # Edge detection for structure analysis
            edges = cv2.Canny(gray, 50, 150, apertureSize=3)

            # Find contours for element detection
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Analyze composition using rule of thirds
            height, width = gray.shape
            thirds_h = [height // 3, 2 * height // 3]
            thirds_w = [width // 3, 2 * width // 3]

            # Calculate visual weight distribution
            total_pixels = height * width
            upper_third = np.sum(gray[:thirds_h[0], :]) / (thirds_h[0] * width)
            middle_third = np.sum(gray[thirds_h[0]:thirds_h[1], :]) / ((thirds_h[1] - thirds_h[0]) * width)
            lower_third = np.sum(gray[thirds_h[1]:, :]) / ((height - thirds_h[1]) * width)

            return {
                "dimensions": {"width": width, "height": height},
                "aspect_ratio": round(width / height, 2),
                "edge_density": len(contours),
                "composition_analysis": {
                    "rule_of_thirds_lines": {"horizontal": thirds_h, "vertical": thirds_w},
                    "visual_weight_distribution": {
                        "upper": float(upper_third),
                        "middle": float(middle_third), 
                        "lower": float(lower_third)
                    }
                },
                "structural_elements": len([c for c in contours if cv2.contourArea(c) > 100])
            }

        except Exception as e:
            logger.error("Layout analysis failed", error=str(e))
            return {"error": "Layout analysis unavailable"}

    async def _extract_text_elements(self, image_array: np.ndarray) -> List[Dict[str, Any]]:
        """Extract and analyze text elements in the image."""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)

            # Simple text region detection using MSER
            mser = cv2.MSER_create()
            regions, _ = mser.detectRegions(gray)

            text_elements = []
            for i, region in enumerate(regions[:10]):  # Limit to first 10 regions
                # Get bounding box
                x, y, w, h = cv2.boundingRect(region.reshape(-1, 1, 2))

                # Basic validation for text-like regions
                if w > 10 and h > 10 and w / h < 10:  # Reasonable aspect ratio
                    text_elements.append({
                        "id": i,
                        "bbox": [int(x), int(y), int(w), int(h)],
                        "area": int(w * h),
                        "confidence": 0.7,  # Placeholder confidence
                        "type": "potential_text"
                    })

            return text_elements

        except Exception as e:
            logger.error("Text extraction failed", error=str(e))
            return []

    async def _detect_ui_components(self, image_array: np.ndarray) -> List[Dict[str, Any]]:
        """Detect UI components like buttons, forms, navigation elements."""
        try:
            # Convert to grayscale and apply preprocessing
            gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)

            # Detect rectangular components (potential buttons, cards, etc.)
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            ui_components = {
                "buttons": [],
                "cards": [],
                "forms": [],
                "navigation": [],
                "images": []
            }

            for i, contour in enumerate(contours):
                # Get bounding rectangle
                x, y, w, h = cv2.boundingRect(contour)
                area = cv2.contourArea(contour)

                if area < 100:  # Skip very small components
                    continue

                # Classify based on shape and size heuristics
                aspect_ratio = w / h if h > 0 else 0

                component = {
                    "id": i,
                    "bbox": [int(x), int(y), int(w), int(h)],
                    "area": int(area),
                    "aspect_ratio": round(aspect_ratio, 2)
                }

                # Simple heuristic-based classification
                if 0.3 <= aspect_ratio <= 4 and 1000 <= area <= 10000:
                    ui_components["buttons"].append(component)
                elif aspect_ratio > 0.5 and area > 5000:
                    ui_components["cards"].append(component)
                elif aspect_ratio > 2 and area > 2000:
                    ui_components["navigation"].append(component)
                else:
                    ui_components["images"].append(component)

            return [ui_components]

        except Exception as e:
            logger.error("UI component detection failed", error=str(e))
            return []

    def validate_image(self, image_bytes: bytes) -> bool:
        """Validate image format and size."""
        try:
            if len(image_bytes) > settings.max_image_size:
                return False

            image = Image.open(io.BytesIO(image_bytes))
            format_valid = image.format.lower() in [f.upper() for f in settings.supported_image_formats]

            return format_valid and image.width > 0 and image.height > 0

        except Exception:
            return False
