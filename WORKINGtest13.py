import cv2
import numpy as np
from shapely.geometry import Polygon, Point
from PIL import Image, ImageDraw, ImageFont
from shapely.ops import unary_union

FONT_SIZE = 12
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
INPAINT_RGB = (200, 200, 255)  # Matches OpenCV's (255, 200, 200) in RGB


def merge_vertical_japanese_lines(polygons, gap_threshold=15):
    def get_bounds(poly):
        xs = [p[0] for p in poly]
        ys = [p[1] for p in poly]
        return min(xs), max(xs), min(ys), max(ys)

    sorted_polys = sorted(polygons, key=lambda p: sum(pt[0] for pt in p) / len(p))
    merged_polys = []

    for i in range(len(sorted_polys)):
        curr = sorted_polys[i]
        cx_min, cx_max, cy_min, cy_max = get_bounds(curr)
        merged_polys.append(Polygon([
            (cx_min - 2, cy_min - 2),
            (cx_max + 2, cy_min - 2),
            (cx_max + 2, cy_max + 2),
            (cx_min - 2, cy_max + 2)
        ]))

        if i < len(sorted_polys) - 1:
            nxt = sorted_polys[i + 1]
            nx_min, nx_max, ny_min, ny_max = get_bounds(nxt)
            hgap = nx_min - cx_max
            if hgap > gap_threshold:
                continue

            height1 = cy_max - cy_min
            height2 = ny_max - ny_min
            patch_height = min(height1, height2)

            shared_y_top = max(cy_min, ny_min)
            shared_y_bottom = min(cy_max, ny_max)
            mid_y = (shared_y_top + shared_y_bottom) // 2

            y1 = mid_y - patch_height // 2
            y2 = mid_y + patch_height // 2
            y1 = max(y1, 0)
            y2 = max(y2, y1 + 1)

            gap_box = Polygon([
                (cx_max, y1),
                (nx_min, y1),
                (nx_min, y2),
                (cx_max, y2)
            ])
            merged_polys.append(gap_box)

    unified = unary_union(merged_polys)
    if unified.geom_type == "Polygon":
        return [unified]
    else:
        return list(unified.geoms)


def draw_text_inside_polygon(img_pil, polygon: Polygon, text: str, font_path: str):
    draw = ImageDraw.Draw(img_pil)
    font = ImageFont.truetype(font_path, FONT_SIZE)

    minx, miny, maxx, maxy = map(int, polygon.bounds)
    line_height = FONT_SIZE + 4
    y_cursor = miny
    text_cursor = 0

    current_word = ""
    current_word_positions = []
    in_word = False
    next_line_hyphen = False
    erased_char = None
    erased_char_fontbox = None

    while y_cursor + line_height <= maxy and text_cursor < len(text):
        x = minx
        segments = []
        inside = False
        seg_start = None

        while x <= maxx:
            point = Point(x, y_cursor + FONT_SIZE // 2)
            if polygon.contains(point):
                if not inside:
                    seg_start = x
                    inside = True
            else:
                if inside:
                    segments.append((seg_start, x))
                    inside = False
            x += 1
        if inside:
            segments.append((seg_start, x))

        for start_x, end_x in segments:
            curr_x = start_x
            while text_cursor < len(text):
                char = text[text_cursor]

                if char == "\n":
                    text_cursor += 1
                    break

                # If line just broke mid-word, add hyphen at start
                if next_line_hyphen:
                    bbox = draw.textbbox((0, 0), "-", font=font)
                    dash_width = bbox[2] - bbox[0]
                    draw.text((curr_x, y_cursor), "-", font=font, fill=(0, 0, 0))
                    curr_x += dash_width

                    # Redraw the erased character
                    if erased_char and erased_char_fontbox:
                        char_width = erased_char_fontbox[2] - erased_char_fontbox[0]
                        draw.text((curr_x, y_cursor), erased_char, font=font, fill=(0, 0, 0))
                        curr_x += char_width
                        # reset
                        erased_char = None
                        erased_char_fontbox = None

                    next_line_hyphen = False

                bbox = draw.textbbox((0, 0), char, font=font)
                char_width = bbox[2] - bbox[0]

                if curr_x + char_width > end_x:
                    break  # move to next segment

                center_point = Point(curr_x + char_width // 2, y_cursor + FONT_SIZE // 2)
                if polygon.contains(center_point):
                    draw.text((curr_x, y_cursor), char, font=font, fill=(0, 0, 0))

                    if char != " ":
                        if not in_word:
                            in_word = True
                            current_word = ""
                            current_word_positions = []
                        current_word += char
                        current_word_positions.append((curr_x, y_cursor, char_width))
                    else:
                        in_word = False
                        current_word = ""
                        current_word_positions = []

                    curr_x += char_width
                    text_cursor += 1
                else:
                    curr_x += 1  # shift right to find a better spot

        # End of the line: if we were mid-word, hyphenate
        if in_word:
            in_word = False
            if current_word and len(current_word_positions) >= 1:
                last_x, last_y, last_w = current_word_positions[-1]
                erased_char = current_word[-1]
                erased_char_fontbox = draw.textbbox((0, 0), erased_char, font=font)

                draw.rectangle([last_x, last_y, last_x + last_w, last_y + FONT_SIZE + 1], fill=INPAINT_RGB)
                draw.text((last_x, last_y), "-", font=font, fill=(0, 0, 0))

                next_line_hyphen = True
                current_word = ""
                current_word_positions = []

        y_cursor += line_height

    return img_pil


def inpaint_and_draw_text(image_path, polygons, output_path, text):
    img = cv2.imread(image_path)
    if img is None:
        print("Image load failed:", image_path)
        return

    height, width = img.shape[:2]
    mask = np.zeros((height, width), dtype=np.uint8)

    merged_polygons = merge_vertical_japanese_lines(polygons)

    for poly in merged_polygons:
        pts = np.array([list(poly.exterior.coords)], dtype=np.int32)
        cv2.fillPoly(img, pts, (255, 200, 200))  # light red

    img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

    for poly in merged_polygons:
        img_pil = draw_text_inside_polygon(img_pil, poly, text, FONT_PATH)

    final = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
    cv2.imwrite(output_path, final)
    cv2.imshow("Text Inside Polygon", final)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


# Run
if __name__ == "__main__":
    image_path = "/home/shivi/fuckYOU/test7.png"
    output_path = "text_wrapped_inside_polygon.jpg"
    polygons = [
        [[192, 9], [223, 9], [223, 120], [192, 120]],
        [[228, 9], [258, 9], [258, 276], [228, 276]],
        [[263, 9], [295, 9], [295, 222], [263, 222]],
        [[497, 7], [528, 7], [528, 208], [497, 208]],
    ]
    sample_text = "hi"
    inpaint_and_draw_text(image_path, polygons, output_path, sample_text)
