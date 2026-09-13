"""
Thumbnail Text Overlay - Add text, numbers, and CTAs to thumbnail images.
Uses PIL to add readable, high-contrast text overlays optimized for YouTube.
"""

from PIL import Image, ImageDraw, ImageFont
import os
from utils import setup_logger

logger = setup_logger("ThumbnailTextOverlay")


class ThumbnailTextOverlay:
    """Add text overlays to thumbnail images."""

    FONT_SIZES = {
        'title': 60,
        'number': 80,
        'cta': 40,
        'small': 30
    }

    COLORS = {
        'white': (255, 255, 255),
        'black': (0, 0, 0),
        'red': (255, 50, 50),
        'yellow': (255, 255, 0),
        'blue': (0, 150, 255),
        'green': (50, 255, 50),
        'orange': (255, 165, 0),
    }

    def __init__(self):
        """Initialize text overlay engine."""
        logger.info(f"📝 Text overlay engine initialized")

    def add_text_to_image(self, image_path, text, position="center",
                         font_size="title", color="white", outline=True,
                         output_path=None):
        """
        Add text to a thumbnail image.

        Args:
            image_path: Path to thumbnail image
            text: Text to add
            position: "top", "center", "bottom", or (x, y) tuple
            font_size: "title", "number", "cta", "small", or int
            color: Color name or (R, G, B) tuple
            outline: Add black outline for readability?
            output_path: Where to save result (default: overwrite input)

        Returns:
            Path to image with text overlay
        """
        logger.info(f"📝 Adding text to image: '{text}'")

        if not os.path.exists(image_path):
            logger.error(f"❌ Image not found: {image_path}")
            raise FileNotFoundError(image_path)

        try:
            # Open image
            img = Image.open(image_path).convert('RGB')
            draw = ImageDraw.Draw(img)
            width, height = img.size

            # Parse font size
            if isinstance(font_size, str):
                font_size_px = self.FONT_SIZES.get(font_size, 60)
            else:
                font_size_px = font_size

            # Try to load system font (fallback to default)
            try:
                font = ImageFont.truetype("arial.ttf", font_size_px)
            except:
                try:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size_px)
                except:
                    font = ImageFont.load_default()
                    logger.warning("⚠️  Using default font (install PIL fonts for better results)")

            # Parse color
            if isinstance(color, str):
                rgb_color = self.COLORS.get(color, self.COLORS['white'])
            else:
                rgb_color = color

            # Calculate position
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            if isinstance(position, str):
                if position == "top":
                    x = (width - text_width) // 2
                    y = height // 8
                elif position == "center":
                    x = (width - text_width) // 2
                    y = (height - text_height) // 2
                elif position == "bottom":
                    x = (width - text_width) // 2
                    y = height - height // 8 - text_height
                else:
                    x = (width - text_width) // 2
                    y = (height - text_height) // 2
            else:
                x, y = position

            # Draw with outline for readability
            if outline:
                outline_width = 3
                for adj_x in range(-outline_width, outline_width + 1):
                    for adj_y in range(-outline_width, outline_width + 1):
                        draw.text((x + adj_x, y + adj_y), text, font=font,
                                fill=self.COLORS['black'])

            # Draw main text
            draw.text((x, y), text, font=font, fill=rgb_color)

            # Save
            if output_path is None:
                output_path = image_path

            img.save(output_path, quality=95)
            logger.info(f"✓ Text overlay added and saved to {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"❌ Text overlay failed: {e}")
            raise

    def add_number_badge(self, image_path, number, position="top_left",
                        color="red", output_path=None):
        """
        Add a number badge (like "7 Ways" videos) to thumbnail.

        Args:
            image_path: Path to thumbnail
            number: Number to display (int or str)
            position: "top_left", "top_right", "bottom_left", "bottom_right"
            color: Badge color
            output_path: Output path

        Returns:
            Path to image with badge
        """
        logger.info(f"🔢 Adding number badge: {number}")

        try:
            img = Image.open(image_path).convert('RGB')
            draw = ImageDraw.Draw(img)
            width, height = img.size

            # Font for number
            try:
                font = ImageFont.truetype("arial.ttf", self.FONT_SIZES['number'])
            except:
                font = ImageFont.load_default()

            text = str(number)
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            # Circle size
            circle_radius = max(text_width, text_height) // 2 + 20

            # Position
            margin = 20
            if position == "top_left":
                circle_x, circle_y = circle_radius + margin, circle_radius + margin
            elif position == "top_right":
                circle_x, circle_y = width - circle_radius - margin, circle_radius + margin
            elif position == "bottom_left":
                circle_x, circle_y = circle_radius + margin, height - circle_radius - margin
            else:  # bottom_right
                circle_x, circle_y = width - circle_radius - margin, height - circle_radius - margin

            # Draw circle background
            rgb_color = self.COLORS.get(color, self.COLORS['red'])
            draw.ellipse(
                [(circle_x - circle_radius, circle_y - circle_radius),
                 (circle_x + circle_radius, circle_y + circle_radius)],
                fill=rgb_color,
                outline=self.COLORS['white'],
                width=3
            )

            # Draw number
            text_x = circle_x - text_width // 2
            text_y = circle_y - text_height // 2
            draw.text((text_x, text_y), text, font=font, fill=self.COLORS['white'])

            # Save
            if output_path is None:
                output_path = image_path

            img.save(output_path, quality=95)
            logger.info(f"✓ Number badge added")
            return output_path

        except Exception as e:
            logger.error(f"❌ Badge creation failed: {e}")
            raise

    def add_cta_banner(self, image_path, cta_text, position="bottom",
                      background_color="red", text_color="white", output_path=None):
        """
        Add a CTA (call-to-action) banner to thumbnail.

        Args:
            image_path: Path to thumbnail
            cta_text: Text like "WATCH NOW", "CLICK HERE"
            position: "top" or "bottom"
            background_color: Banner background color
            text_color: Text color
            output_path: Output path

        Returns:
            Path to image with CTA banner
        """
        logger.info(f"🎯 Adding CTA banner: {cta_text}")

        try:
            img = Image.open(image_path).convert('RGB')
            draw = ImageDraw.Draw(img)
            width, height = img.size

            # Font for CTA
            try:
                font = ImageFont.truetype("arial.ttf", self.FONT_SIZES['cta'])
            except:
                font = ImageFont.load_default()

            bg_color = self.COLORS.get(background_color, self.COLORS['red'])
            txt_color = self.COLORS.get(text_color, self.COLORS['white'])

            # Banner dimensions
            banner_height = height // 8
            bbox = draw.textbbox((0, 0), cta_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            # Position
            if position == "top":
                banner_y = 0
                text_y = (banner_height - text_height) // 2
            else:  # bottom
                banner_y = height - banner_height
                text_y = banner_y + (banner_height - text_height) // 2

            # Draw banner
            draw.rectangle(
                [(0, banner_y), (width, banner_y + banner_height)],
                fill=bg_color
            )

            # Draw text
            text_x = (width - text_width) // 2
            draw.text((text_x, text_y), cta_text, font=font, fill=txt_color)

            # Save
            if output_path is None:
                output_path = image_path

            img.save(output_path, quality=95)
            logger.info(f"✓ CTA banner added")
            return output_path

        except Exception as e:
            logger.error(f"❌ CTA banner creation failed: {e}")
            raise

    def add_arrow(self, image_path, position="top_left", color="yellow", output_path=None):
        """
        Add an arrow to draw attention to specific area.

        Args:
            image_path: Path to thumbnail
            position: "top_left", "top_right", "center", etc.
            color: Arrow color
            output_path: Output path

        Returns:
            Path to image with arrow
        """
        logger.info(f"➡️  Adding arrow: {position}")

        try:
            img = Image.open(image_path).convert('RGB')
            draw = ImageDraw.Draw(img)
            width, height = img.size

            arrow_color = self.COLORS.get(color, self.COLORS['yellow'])
            arrow_size = min(width, height) // 6

            # Arrow coordinates based on position
            if position == "top_left":
                start_x, start_y = width // 4, height // 4
                end_x, end_y = width // 2, height // 2
            elif position == "center":
                start_x, start_y = width // 2, height // 3
                end_x, end_y = width // 2 + arrow_size, height // 2
            else:  # default
                start_x, start_y = width // 2, height // 3
                end_x, end_y = width // 2 + arrow_size, height // 2

            # Draw arrow line with thick stroke
            draw.line([(start_x, start_y), (end_x, end_y)],
                     fill=arrow_color, width=8)

            # Draw arrowhead
            angle_rad = __import__('math').atan2(end_y - start_y, end_x - start_x)
            arrow_length = arrow_size // 2

            import math
            head_x1 = end_x - arrow_length * math.cos(angle_rad - math.pi / 6)
            head_y1 = end_y - arrow_length * math.sin(angle_rad - math.pi / 6)
            head_x2 = end_x - arrow_length * math.cos(angle_rad + math.pi / 6)
            head_y2 = end_y - arrow_length * math.sin(angle_rad + math.pi / 6)

            draw.polygon([(end_x, end_y), (head_x1, head_y1), (head_x2, head_y2)],
                        fill=arrow_color)

            # Save
            if output_path is None:
                output_path = image_path

            img.save(output_path, quality=95)
            logger.info(f"✓ Arrow added")
            return output_path

        except Exception as e:
            logger.error(f"❌ Arrow creation failed: {e}")
            raise

    def print_overlay_options(self):
        """Print available text overlay options."""
        print("\n" + "=" * 60)
        print("TEXT OVERLAY OPTIONS")
        print("=" * 60)

        print("\n📍 Positions:")
        print("  - top, center, bottom (auto-centered)")
        print("  - (x, y) tuple for custom position")

        print("\n📐 Font Sizes:")
        for size_name, size_px in self.FONT_SIZES.items():
            print(f"  - {size_name}: {size_px}px")

        print("\n🎨 Colors:")
        for color_name in self.COLORS.keys():
            print(f"  - {color_name}")

        print("\n" + "=" * 60 + "\n")
