"""
Generate PNG icons from SVG for PWA
Run this script to create PNG versions of the icons
"""
try:
    from cairosvg import svg2png
    import os
    
    # Get the static directory path
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    
    # Convert 192x192 icon
    svg2png(
        url=os.path.join(static_dir, 'icon-192.svg'),
        write_to=os.path.join(static_dir, 'icon-192.png'),
        output_width=192,
        output_height=192
    )
    print("✅ Created icon-192.png")
    
    # Convert 512x512 icon
    svg2png(
        url=os.path.join(static_dir, 'icon-512.svg'),
        write_to=os.path.join(static_dir, 'icon-512.png'),
        output_width=512,
        output_height=512
    )
    print("✅ Created icon-512.png")
    
    print("\n🎉 PWA icons generated successfully!")
    print("You can now use the app as a PWA on iPhone/iPad")
    
except ImportError:
    print("⚠️  cairosvg not installed. Using SVG icons directly.")
    print("To generate PNG icons, install cairosvg:")
    print("pip install cairosvg")
    print("\nNote: SVG icons will work fine for most browsers!")
