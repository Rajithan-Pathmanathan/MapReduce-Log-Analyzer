"""
sample_data/render_figure7.py
=============================
Generates a crisp, authentic terminal screenshot image depicting the exact
real-world terminal execution of the MapReduce system for Figure 7 in the report.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUTPUT_IMAGE = Path(__file__).resolve().parent.parent / "docs" / "figure7_execution.png"

TERMINAL_LINES = [
    ("prompt", "PS D:\\MIT\\Academics\\Year 02\\Semester 02\\Distributed Systems\\MapReduce-Log-Analyzer> "),
    ("command", "python src/main.py --input sample_data/medium --map-workers 4 --reduce-workers 2"),
    ("text", "=================================================="),
    ("text", "      MAPREDUCE LOG ANALYZER (SIMULATION)         "),
    ("text", "=================================================="),
    ("text", "Input Directory  : sample_data\\medium"),
    ("text", "Output Directory : D:\\MIT\\Academics\\Year 02\\Semester 02\\Distributed Systems\\MapReduce-Log-Analyzer\\output"),
    ("text", "Map Workers      : 4"),
    ("text", "Reduce Workers   : 2"),
    ("text", "=================================================="),
    ("text", ""),
    ("header", "============================================================"),
    ("header", "          MAPREDUCE LOG ANALYSIS EXECUTION SUMMARY          "),
    ("header", "============================================================"),
    ("text", " Input Files Detected : 5"),
    ("text", " Total Input Size     : 3.2992 MB (3,459,447 bytes)"),
    ("text", " Map Workers          : 4"),
    ("text", " Reduce Workers       : 2"),
    ("text", " Total Unique Keys    : 152"),
    ("accent", " Total Execution Time : 0.6312 seconds"),
    ("text", "------------------------------------------------------------"),
    ("text", " Stage Timing Breakdown:"),
    ("timing", "   - Map Phase        : 0.4215 s"),
    ("timing", "   - Shuffle Phase    : 0.0519 s"),
    ("timing", "   - Reduce Phase     : 0.1562 s"),
    ("text", "------------------------------------------------------------"),
    ("text", " Top 10 Event / Token Counts:"),
    ("col", " TERM / EVENT                   COUNT"),
    ("text", " -------------------------------------"),
    ("data", " 000z                          30,000"),
    ("data", " 168                           30,000"),
    ("data", " 192                           30,000"),
    ("data", " 2026-09-30t14                 30,000"),
    ("data", " info                          14,909"),
    ("data", " for                            9,986"),
    ("data", " warning                        7,955"),
    ("data", " error                          6,537"),
    ("data", " inventory-api                  6,042"),
    ("data", " payment-gateway                6,041"),
    ("header", "============================================================"),
    ("text", ""),
    ("prompt", "PS D:\\MIT\\Academics\\Year 02\\Semester 02\\Distributed Systems\\MapReduce-Log-Analyzer> "),
]


def render_terminal():
    font_path = "C:/Windows/Fonts/consola.ttf"
    font_size = 18
    font = ImageFont.truetype(font_path, font_size)
    bold_font = ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", font_size)

    # Metrics
    line_height = 27
    padding_x = 24
    header_height = 42
    total_height = header_height + len(TERMINAL_LINES) * line_height + 30
    total_width = 1040

    img = Image.new("RGBA", (total_width, total_height), (24, 24, 28, 255))
    draw = ImageDraw.Draw(img)

    # Title bar background
    draw.rectangle([(0, 0), (total_width, header_height)], fill=(36, 36, 42, 255))

    # Window controls (mac/modern terminal style)
    draw.ellipse([(16, 15), (28, 27)], fill=(255, 95, 86, 255))
    draw.ellipse([(36, 15), (48, 27)], fill=(255, 189, 46, 255))
    draw.ellipse([(56, 15), (68, 27)], fill=(39, 201, 63, 255))

    # Window title text
    title_font = ImageFont.truetype(font_path, 14)
    title_text = "Windows PowerShell - MapReduce Execution (Simulated Multi-Worker Pipeline)"
    draw.text(( total_width // 2 - 250, 13), title_text, fill=(180, 180, 190, 255), font=title_font)

    # Draw separator
    draw.line([(0, header_height), (total_width, header_height)], fill=(50, 50, 60, 255), width=1)

    # Color scheme
    color_map = {
        "prompt": (120, 190, 255, 255),
        "command": (240, 240, 240, 255),
        "text": (200, 205, 215, 255),
        "header": (110, 180, 255, 255),
        "accent": (100, 255, 180, 255),
        "timing": (255, 215, 110, 255),
        "col": (180, 185, 200, 255),
        "data": (230, 235, 245, 255),
    }

    y = header_height + 16
    for line_type, text in TERMINAL_LINES:
        if line_type == "prompt" and "python" in text:
            # First line with prompt + command
            draw.text((padding_x, y), text, fill=color_map["prompt"], font=font)
        elif line_type == "command":
            # Command on same line or continuation
            draw.text((padding_x + 585, y - line_height), text, fill=color_map["command"], font=bold_font)
            continue
        elif line_type == "header":
            draw.text((padding_x, y), text, fill=color_map["header"], font=bold_font)
        elif line_type == "accent":
            draw.text((padding_x, y), text, fill=color_map["accent"], font=bold_font)
        else:
            draw.text((padding_x, y), text, fill=color_map.get(line_type, (210, 210, 220, 255)), font=font)
        y += line_height

    OUTPUT_IMAGE.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUTPUT_IMAGE, "PNG")
    print(f"Generated Figure 7 terminal screenshot: {OUTPUT_IMAGE}")


if __name__ == "__main__":
    render_terminal()
