#!/usr/bin/env python3
"""
Instagram Text Image Generator
Creates professional-looking images from text for Instagram posts
"""

from PIL import Image, ImageDraw, ImageFont
import textwrap
from pathlib import Path


class InstagramImageGenerator:
    def __init__(self):
        # Instagram optimal size: 1080x1080 (square)
        self.width = 1080
        self.height = 1080
        self.bg_color = (45, 52, 54)  # Dark gray
        self.text_color = (255, 255, 255)  # White
        self.accent_color = (255, 107, 107)  # Coral red

    def create_text_image(self, text, output_path):
        """Create an image with text"""
        # Create image with gradient background
        img = Image.new('RGB', (self.width, self.height), self.bg_color)
        draw = ImageDraw.Draw(img)

        # Add gradient effect (simple version)
        for y in range(self.height):
            alpha = y / self.height
            color = tuple(int(self.bg_color[i] + (self.accent_color[i] - self.bg_color[i]) * alpha * 0.3) for i in range(3))
            draw.line([(0, y), (self.width, y)], fill=color)

        # Try to load a nice font, fallback to default
        try:
            # Try common font locations
            font_paths = [
                "C:/Windows/Fonts/arial.ttf",
                "C:/Windows/Fonts/calibri.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                "/System/Library/Fonts/Helvetica.ttc",
            ]

            font = None
            for font_path in font_paths:
                if Path(font_path).exists():
                    font = ImageFont.truetype(font_path, 48)
                    break

            if not font:
                font = ImageFont.load_default()
        except:
            font = ImageFont.load_default()

        # Wrap text to fit width
        margin = 80
        max_width = self.width - (margin * 2)

        # Split text into lines
        lines = []
        for paragraph in text.split('\n'):
            if paragraph.strip():
                # Wrap each paragraph
                wrapped = textwrap.fill(paragraph, width=35)  # ~35 chars per line
                lines.extend(wrapped.split('\n'))
            else:
                lines.append('')

        # Calculate total text height
        line_height = 60
        total_height = len(lines) * line_height

        # Start position (centered vertically)
        y = (self.height - total_height) // 2

        # Draw each line
        for line in lines:
            # Get text size for centering
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]

            # Center horizontally
            x = (self.width - text_width) // 2

            # Draw text with shadow for better readability
            shadow_offset = 3
            draw.text((x + shadow_offset, y + shadow_offset), line, font=font, fill=(0, 0, 0, 128))
            draw.text((x, y), line, font=font, fill=self.text_color)

            y += line_height

        # Add decorative elements
        # Top border
        draw.rectangle([(40, 40), (self.width - 40, 50)], fill=self.accent_color)
        # Bottom border
        draw.rectangle([(40, self.height - 50), (self.width - 40, self.height - 40)], fill=self.accent_color)

        # Save image
        img.save(output_path, quality=95)
        print(f"[IMAGE] Generated: {output_path}")
        return output_path


def generate_instagram_image(caption_text, output_filename="instagram_post.jpg"):
    """Generate an Instagram image from caption text"""
    generator = InstagramImageGenerator()

    # Clean up caption (remove hashtags for image, keep them for caption)
    lines = caption_text.split('\n')
    text_lines = []

    for line in lines:
        # Skip lines that are mostly hashtags
        if line.strip().startswith('#'):
            continue
        # Remove emojis and special characters that might not render well
        clean_line = line.strip()
        if clean_line:
            text_lines.append(clean_line)

    # Join lines with proper spacing
    clean_text = '\n'.join(text_lines)

    # Limit text length for readability
    if len(clean_text) > 400:
        clean_text = clean_text[:400] + "..."

    # Generate image
    output_path = Path(output_filename)
    generator.create_text_image(clean_text, output_path)

    return output_path


if __name__ == "__main__":
    # Test the generator
    test_text = """💡 What if your business could run itself while you sleep?

We just built an AI assistant that actually works like a real employee:

📧 Reads emails → Drafts replies
💬 Monitors WhatsApp → Responds to customers
📱 Creates social posts → Schedules content
📊 Handles workflows → Makes decisions

Built in 48 hours at the hackathon. Now running 24/7.

The future isn't coming. It's already here. 🚀"""

    output = generate_instagram_image(test_text, "test_instagram_post.jpg")
    print(f"Test image created: {output}")
