from pathlib import Path
import minify_html


def css(css_dir: Path | str = "css", site_dir: Path | str = Path("build/site")) -> None:
    """
    Read CSS files from a directory, minify them using minify-html, and write to the site directory.

    Args:
        css_dir: Directory containing CSS files. Defaults to "css"
        site_dir: Directory to write minified CSS files. Defaults to "build/site"

    Raises:
        OSError: If there are issues creating directories or reading/writing files
    """
    css_dir = Path(css_dir)
    site_dir = Path(site_dir)
    
    # Create the output CSS directory
    css_output_dir = site_dir / "css"
    css_output_dir.mkdir(parents=True, exist_ok=True)
    
    # Process each CSS file
    if not css_dir.exists():
        return
        
    for css_file in css_dir.glob("*.css"):
        # Read and minify CSS content
        css_content = css_file.read_text(encoding="utf-8")
        minified_css = minify_html.minify(css_content, minify_css=True)
        
        # Write minified content to output directory
        output_file = css_output_dir / css_file.name
        output_file.write_text(minified_css, encoding="utf-8")
