"""
Thumbnail Optimizer - Optimize thumbnails for YouTube specifications.
Handles resizing, format conversion, quality optimization.
"""

import os
from PIL import Image
from utils import setup_logger

logger = setup_logger("ThumbnailOptimizer")


class ThumbnailOptimizer:
    """Optimize thumbnails for YouTube and social media platforms."""

    YOUTUBE_SPECS = {
        'standard': {
            'dimensions': (1280, 720),
            'aspect_ratio': '16:9',
            'min_size': (640, 360),
            'max_size': (1920, 1080),
            'formats': ['JPG', 'PNG'],
            'max_file_size_mb': 2
        },
        'square': {
            'dimensions': (1200, 1200),
            'aspect_ratio': '1:1',
            'min_size': (600, 600),
            'max_size': (1920, 1920),
            'formats': ['JPG', 'PNG'],
            'max_file_size_mb': 2
        },
        'shorts': {
            'dimensions': (1080, 1920),
            'aspect_ratio': '9:16',
            'min_size': (540, 960),
            'max_size': (1080, 1920),
            'formats': ['JPG', 'PNG'],
            'max_file_size_mb': 2
        }
    }

    def __init__(self):
        """Initialize thumbnail optimizer."""
        logger.info(f"🔧 Thumbnail optimizer initialized")

    def validate_thumbnail(self, image_path, platform='youtube_standard'):
        """
        Validate thumbnail meets platform specifications.

        Args:
            image_path: Path to thumbnail image
            platform: 'youtube_standard', 'youtube_square', 'youtube_shorts'

        Returns:
            Validation result dict with issues and warnings
        """
        logger.info(f"✓ Validating thumbnail for {platform}")

        if not os.path.exists(image_path):
            return {'valid': False, 'error': 'File not found'}

        try:
            img = Image.open(image_path)
            width, height = img.size
            file_size_mb = os.path.getsize(image_path) / (1024 * 1024)
            format_used = img.format

            specs = self.YOUTUBE_SPECS.get(platform.replace('youtube_', ''), self.YOUTUBE_SPECS['standard'])

            issues = []
            warnings = []

            # Check dimensions
            if (width, height) != specs['dimensions']:
                warnings.append(f"Dimensions {width}x{height}, ideal: {specs['dimensions'][0]}x{specs['dimensions'][1]}")

            # Check minimum size
            if width < specs['min_size'][0] or height < specs['min_size'][1]:
                issues.append(f"Image too small (min: {specs['min_size'][0]}x{specs['min_size'][1]})")

            # Check maximum size
            if width > specs['max_size'][0] or height > specs['max_size'][1]:
                issues.append(f"Image too large (max: {specs['max_size'][0]}x{specs['max_size'][1]})")

            # Check format
            if format_used not in specs['formats']:
                warnings.append(f"Format {format_used}, recommended: {', '.join(specs['formats'])}")

            # Check file size
            if file_size_mb > specs['max_file_size_mb']:
                warnings.append(f"File size {file_size_mb:.2f}MB, max: {specs['max_file_size_mb']}MB")

            result = {
                'valid': len(issues) == 0,
                'dimensions': (width, height),
                'format': format_used,
                'file_size_mb': file_size_mb,
                'issues': issues,
                'warnings': warnings,
                'status': 'PASS' if len(issues) == 0 else 'FAIL'
            }

            logger.info(f"✓ Validation complete: {result['status']}")
            return result

        except Exception as e:
            logger.error(f"❌ Validation failed: {e}")
            return {'valid': False, 'error': str(e)}

    def resize_thumbnail(self, image_path, target_dimensions, maintain_aspect=True,
                        output_path=None):
        """
        Resize thumbnail to specific dimensions.

        Args:
            image_path: Path to source image
            target_dimensions: (width, height) tuple
            maintain_aspect: If True, add padding to maintain aspect ratio
            output_path: Where to save result

        Returns:
            Path to resized image
        """
        logger.info(f"📐 Resizing to {target_dimensions[0]}x{target_dimensions[1]}")

        try:
            img = Image.open(image_path).convert('RGB')
            original_width, original_height = img.size
            target_width, target_height = target_dimensions

            if maintain_aspect:
                # Calculate scaling to maintain aspect ratio
                scale_x = target_width / original_width
                scale_y = target_height / original_height
                scale = min(scale_x, scale_y)

                # Resize
                new_width = int(original_width * scale)
                new_height = int(original_height * scale)
                img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

                # Create background
                background = Image.new('RGB', target_dimensions, (0, 0, 0))

                # Paste resized image centered
                offset_x = (target_width - new_width) // 2
                offset_y = (target_height - new_height) // 2
                background.paste(img_resized, (offset_x, offset_y))

                result_img = background
            else:
                # Direct resize (may distort)
                result_img = img.resize(target_dimensions, Image.Resampling.LANCZOS)

            # Save
            if output_path is None:
                base, ext = os.path.splitext(image_path)
                output_path = f"{base}_resized.jpg"

            result_img.save(output_path, 'JPEG', quality=95)
            logger.info(f"✓ Resized and saved to {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"❌ Resize failed: {e}")
            raise

    def compress_thumbnail(self, image_path, quality=85, target_size_mb=2,
                          output_path=None):
        """
        Compress thumbnail to meet file size requirements.

        Args:
            image_path: Path to image
            quality: JPEG quality (1-100)
            target_size_mb: Target maximum file size
            output_path: Output path

        Returns:
            Path to compressed image
        """
        logger.info(f"📦 Compressing thumbnail...")

        try:
            img = Image.open(image_path).convert('RGB')

            # Try progressively lower quality until size is acceptable
            current_quality = quality
            current_size_mb = os.path.getsize(image_path) / (1024 * 1024)

            if output_path is None:
                base, ext = os.path.splitext(image_path)
                output_path = f"{base}_compressed.jpg"

            while current_size_mb > target_size_mb and current_quality > 50:
                img.save(output_path, 'JPEG', quality=current_quality)
                current_size_mb = os.path.getsize(output_path) / (1024 * 1024)
                current_quality -= 5

            final_size = os.path.getsize(output_path) / (1024 * 1024)
            logger.info(f"✓ Compressed to {final_size:.2f}MB (quality: {current_quality})")
            return output_path

        except Exception as e:
            logger.error(f"❌ Compression failed: {e}")
            raise

    def convert_format(self, image_path, target_format='JPG', output_path=None):
        """
        Convert thumbnail to different format.

        Args:
            image_path: Path to image
            target_format: 'JPG', 'PNG', 'WEBP'
            output_path: Output path

        Returns:
            Path to converted image
        """
        logger.info(f"🔄 Converting to {target_format}...")

        try:
            img = Image.open(image_path).convert('RGB')

            if output_path is None:
                base, _ = os.path.splitext(image_path)
                ext = '.jpg' if target_format == 'JPG' else f".{target_format.lower()}"
                output_path = f"{base}{ext}"

            if target_format == 'JPG':
                img.save(output_path, 'JPEG', quality=95)
            elif target_format == 'PNG':
                img.save(output_path, 'PNG')
            elif target_format == 'WEBP':
                img.save(output_path, 'WEBP', quality=95)
            else:
                raise ValueError(f"Unsupported format: {target_format}")

            logger.info(f"✓ Converted and saved to {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"❌ Conversion failed: {e}")
            raise

    def optimize_for_platform(self, image_path, platform='youtube_standard',
                             output_dir=None):
        """
        Optimize thumbnail for specific platform (resize, compress, format).

        Args:
            image_path: Path to source image
            platform: 'youtube_standard', 'youtube_square', 'youtube_shorts'
            output_dir: Directory to save optimized version

        Returns:
            Path to optimized image
        """
        logger.info(f"🎯 Optimizing for {platform}...")

        try:
            specs = self.YOUTUBE_SPECS.get(platform.replace('youtube_', ''), self.YOUTUBE_SPECS['standard'])
            dimensions = specs['dimensions']

            if output_dir is None:
                output_dir = os.path.dirname(image_path)

            # Step 1: Resize
            resized_path = os.path.join(output_dir, f"{platform}_resized.jpg")
            resized_path = self.resize_thumbnail(image_path, dimensions, output_path=resized_path)

            # Step 2: Compress
            compressed_path = os.path.join(output_dir, f"{platform}_optimized.jpg")
            compressed_path = self.compress_thumbnail(resized_path, quality=95,
                                                     target_size_mb=specs['max_file_size_mb'],
                                                     output_path=compressed_path)

            # Validate
            validation = self.validate_thumbnail(compressed_path, platform)

            if not validation['valid']:
                logger.warning(f"⚠️  Validation issues: {validation['issues']}")

            logger.info(f"✓ Optimization complete")
            return compressed_path

        except Exception as e:
            logger.error(f"❌ Optimization failed: {e}")
            raise

    def create_responsive_thumbnails(self, image_path, output_dir=None):
        """
        Create optimized thumbnails for all major platforms.

        Args:
            image_path: Path to source image
            output_dir: Directory to save variants

        Returns:
            Dict of platform -> optimized image path
        """
        logger.info(f"📱 Creating responsive thumbnails for all platforms...")

        if output_dir is None:
            output_dir = os.path.dirname(image_path)

        results = {}

        for platform in ['youtube_standard', 'youtube_square', 'youtube_shorts']:
            try:
                optimized = self.optimize_for_platform(image_path, platform, output_dir)
                results[platform] = optimized
                logger.info(f"✓ {platform}: {optimized}")
            except Exception as e:
                logger.warning(f"⚠️  {platform} failed: {e}")
                results[platform] = None

        logger.info(f"✓ Created {len([r for r in results.values() if r])} responsive variants")
        return results

    def print_optimization_report(self, validation_result):
        """Print formatted optimization report."""
        print("\n" + "=" * 60)
        print("THUMBNAIL OPTIMIZATION REPORT")
        print("=" * 60)

        print(f"\nStatus: {validation_result.get('status', 'N/A')}")
        print(f"Dimensions: {validation_result.get('dimensions', 'N/A')}")
        print(f"Format: {validation_result.get('format', 'N/A')}")
        print(f"File Size: {validation_result.get('file_size_mb', 0):.2f}MB")

        if validation_result.get('issues'):
            print(f"\n❌ Issues (must fix):")
            for issue in validation_result['issues']:
                print(f"  • {issue}")

        if validation_result.get('warnings'):
            print(f"\n⚠️  Warnings (recommended):")
            for warning in validation_result['warnings']:
                print(f"  • {warning}")

        print("\n" + "=" * 60 + "\n")
