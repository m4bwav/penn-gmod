"""Side-by-side sheet: each screenshot beside the reference photo from about the same viewpoint.
Usage: python tools/compare.py shots/<stamp> [lower|plat|chambers]  -> shots/<stamp>/compare.jpg (compare_<set>.jpg)"""
import os
import sys
from PIL import Image, ImageDraw

PAIRS = {  # shot -> refs/photos file
    "west_balcony": "GCT_Main_Concourse.jpg",
    "east_balcony": "Grand_Central_main_concourse_facing_Apple_agr.jpg",
    "booth": "Grand_Central_Terminal_51214194734.jpg",
    "vault_up": "Grand_Central_Station_Flag_Ceiling.jpg",
    "floor_east": "GCT_east_windows.jpg",
    "stairs_west": "GCT_west_windows.jpg",
}
LOWER = {  # area 2, under the concourse
    "dining": "Grand_Central_Dining_Concourse_Info.jpg",
    "whisper": "Whispering_Gallery.jpg",
    "oyster": "Grand_Central_Oyster_Bar_Grand_Central_Station_NYC.jpg",
}
PLAT = {  # area 4, track platforms
    "plat_head": "Grand_Central_Station_tracks.jpg",
    "car_door": "Metro_North_M7a_Rainbow_Heart_Sticker_Grand_Central.jpg",
}
CHAMBERS = {  # chambers added in the 60-session chain
    "mk_door": "GCT_Market.jpg",
    "mk_dome": "GCT_Market_2.jpg",
    "lex_in": "Lexington_Passage.jpg",
    "gb_in": "Graybar_Passage.jpg",
    "md_conc": "Grand_Central_Madison_Opening_Day_Middle_Concourse.jpg",
    "md_esc": "Grand_Central_Madison_escalators.jpg",
}
d, W, H = sys.argv[1], 640, 400
lower = sys.argv[2:3] and sys.argv[2]
if lower:
    PAIRS = {"lower": LOWER, "plat": PLAT, "chambers": CHAMBERS}[lower]
PAIRS = {k: v for k, v in PAIRS.items() if os.path.exists(f"{d}/{k}.jpg")}  # shots.sh CAMS= may shoot only some
sheet = Image.new("RGB", (W * 2, (H + 18) * len(PAIRS)))
draw = ImageDraw.Draw(sheet)
for i, (shot, ref) in enumerate(PAIRS.items()):
    for j, path in enumerate((f"{d}/{shot}.jpg", f"refs/photos/{ref}")):
        im = Image.open(path).convert("RGB")
        im.thumbnail((W, H))
        sheet.paste(im, (j * W, i * (H + 18)))
        draw.text((j * W + 4, i * (H + 18) + H + 3), path, fill="white")
out = f"{d}/compare_{lower}.jpg" if lower else f"{d}/compare.jpg"
sheet.save(out, quality=85)
print(out)
