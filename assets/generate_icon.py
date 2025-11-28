"""
Generate XENO icon programmatically using PIL
Run this to create icon files if you don't have custom ones
"""
try:
    import os
    from pathlib import Path

    from PIL import Image, ImageDraw, ImageFont

    def create_XENO_icon():
        """Create a simple XENO icon"""
        # Create a 256x256 image with transparency
        size = 256
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Colors
        bg_color = (20, 20, 20, 255)  # Dark background
        accent_color = (0, 212, 255, 255)  # Cyan blue

        # Draw background circle
        margin = 20
        draw.ellipse(
            [margin, margin, size - margin, size - margin],
            fill=bg_color,
            outline=accent_color,
            width=8,
        )

        # Draw "X" in the center
        center = size // 2
        x_size = 80
        thickness = 12

        # First diagonal of X
        draw.line(
            [(center - x_size, center - x_size), (center + x_size, center + x_size)],
            fill=accent_color,
            width=thickness,
        )

        # Second diagonal of X
        draw.line(
            [(center + x_size, center - x_size), (center - x_size, center + x_size)],
            fill=accent_color,
            width=thickness,
        )

        # Add glow effect (outer ring)
        glow_margin = 10
        draw.ellipse(
            [glow_margin, glow_margin, size - glow_margin, size - glow_margin],
            outline=(0, 212, 255, 100),
            width=4,
        )

        # Save as PNG
        assets_dir = Path(__file__).parent
        png_path = assets_dir / "XENO.png"
        img.save(png_path, "PNG")
        print(f"✓ Created {png_path}")

        # Try to save as ICO for Windows
        try:
            # Create multiple sizes for ICO
            sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
            icons = []
            for ico_size in sizes:
                icon_img = img.resize(ico_size, Image.Resampling.LANCZOS)
                icons.append(icon_img)

            ico_path = assets_dir / "XENO.ico"
            icons[0].save(ico_path, format="ICO", sizes=[(s[0], s[1]) for s in sizes])
            print(f"✓ Created {ico_path}")
        except Exception as e:
            print(f"⚠ Could not create .ico file: {e}")
            print("  You can convert XENO.png to .ico online at: https://convertio.co/png-ico/")

        return png_path

    if __name__ == "__main__":
        print("Generating XENO icon...")
        create_XENO_icon()
        print("\n✓ Icon generation complete!")
        print("  You can now use these icons for desktop shortcuts.")

except ImportError:
    print("PIL/Pillow not installed. Install with: pip install pillow")
    print("Or create your own icon and save as assets/XENO.png and assets/XENO.ico")
