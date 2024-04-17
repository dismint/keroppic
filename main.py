# | 🙑  dismint
# | YW5uaWUgPDM=

from PIL import Image, ImageDraw, ImageFont
from math import ceil, floor
from json import load, dump
from os import listdir, path, makedirs

###########
# globals #
###########

defs = {}
database = {} 

verbose = True

filters = {
    "era": "",
    "desc": "",
    "info": "",
    "status": ""
}

####################
# helper functions #
####################

def load_defs():
    global defs

    try:
        with open("defs.json", "r") as f:
            defs = load(f)
        defs["color_mslight"] = tuple(defs["color_mslight"])
        defs["color_mlight"] = tuple(defs["color_mlight"])
        defs["color_mdark"] = tuple(defs["color_mdark"])
        defs["color_high1"] = tuple(defs["color_high1"])
        defs["color_high2"] = tuple(defs["color_high2"])
        defs["color_outline"] = tuple(defs["color_outline"])
        defs["color_have_tint"] = tuple(defs["color_have_tint"])
        defs["color_ship_tint"] = tuple(defs["color_ship_tint"])
        defs["color_join_tint"] = tuple(defs["color_join_tint"])
        defs["color_pay_tint"] = tuple(defs["color_pay_tint"])

    except FileNotFoundError:
        print("expected a defs.json file in the current directory")
        exit(1)

def load_database():
    global database

    try:
        with open("database.json", "r") as f:
            database = load(f)
    except FileNotFoundError:
        pass

def dump_database():
    global database

    with open("database.json", "w") as f:
        dump(database, f, indent=4)

def load_prereqs():
    load_defs()
    load_database()

def get_text(text, font, size, width):
    font = ImageFont.truetype(f"fonts/{font}", size)
    desc_img = Image.new("RGBA", (width, size), (0, 0, 0, 0))
    canvas = ImageDraw.Draw(desc_img)
    canvas.text((0, 0), text, fill=(0, 0, 0, 255), font=font)
    return desc_img

def text_to_lines_fit(text, min_size, max_size, font, constraint):
    cmp = Image.new("L", (1, 1))
    cmp = ImageDraw.Draw(cmp)

    def try_size(size):
        fnt = ImageFont.truetype(f"fonts/{font}", size)
        curword, lines = "", []
        for word in words:
            tmp = curword + f"{word} "
            cmp_len = cmp.textlength(tmp.strip(), fnt)
            if cmp_len > constraint[0]:
                cmp_len = cmp.textlength(curword.strip(), fnt)
                if cmp_len > constraint[0]:
                    return False, []
                lines.append(get_text(curword.strip(), font, size, constraint[0]))
                curword = f"{word} "
            else:
                curword += f"{word} "
        cmp_len = cmp.textlength(curword.strip(), fnt)
        if cmp_len > constraint[0] or (len(lines)+1) * size > constraint[1]:
            return False, []
        lines.append(get_text(curword.strip(), font, size, constraint[0]))

        return True, lines

    # binary search for the largest size that fits
    words, ret = text.split(), []
    while min_size < max_size:
        size = ceil((min_size + max_size) / 2)
        flag, res = try_size(size)
        if flag:
            ret = res
            min_size = size
        else:
            max_size = size - 1

    return max_size, ret

def create_rounded_mask(size, radius):
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, *size), radius=radius, fill=255)
    return mask

def crop_to_ratio(image):
    global defs

    w, h = image.size
    factor = min(floor(w / defs["w_min"]), floor(h / defs["h_min"]))
    w_target, h_target = defs["w_min"] * factor, defs["h_min"] * factor
    w_diff, h_diff = w - w_target, h - h_target
    wl, wr = w_diff // 2, w_diff - w_diff // 2
    ht, hb = h_diff // 2, h_diff - h_diff // 2
    image = image.crop((wl, ht, w-wr, h-hb))
    return image

def scale_to_size(image):
    global defs

    return image.resize((defs["w_desired"], defs["h_desired"]), Image.LANCZOS)

def get_next_available():
    global database

    taken = set()
    for img in database:
        taken.add(int(img))
    for i in range(1000):
        if i not in taken:
            return i

#############
# functions #
#############

def del_img(img):
    global database

    if img not in database:
        return f"file `{img}` does not exist :c"
    del database[img]
    dump_database()
    return f"deleted `{img}`!"

def process_images():
    global database

    files = listdir("img/process")
    files.sort(key=lambda x: int(x.split(".")[0]))
    for file in files:
        name = file.split(".")[0]
        if name in database:
            continue
        image = Image.open(f"img/process/{file}")
        image = crop_to_ratio(image)
        image.save(f"img/cropped/{file}")
        database[name] = {
            "desc": "",
            "section": "",
            "era": "",
            "status": "",
            "info": ""
        }
    dump_database()

def gen_section(section):
    global database
    global filters

    # find images matching section
    img_d, imgs = {}, []
    for img in database:
        if database[img]["section"] == section:
            if database[img]["era"] not in img_d:
                img_d[database[img]["era"]] = []
            img_d[database[img]["era"]].append(img)

    # organize images by era, insert dummy between
    res_folder = f"{defs['w_desired']}x{defs['h_desired']}"
    makedirs(f"img/scaled/{res_folder}", exist_ok=True)
    img_count = 0
    for sub in img_d:
        if filters["era"].upper() not in sub.upper():
            continue
        imgs.append((sub, ""))
        capt = len(imgs)
        for img in img_d[sub]:
            if filters["status"].upper() not in database[img]["status"].upper():
                continue
            if filters["info"].upper() not in database[img]["info"].upper():
                continue
            if filters["desc"].upper() not in database[img]["desc"].upper():
                continue
            if not path.exists(f"img/scaled/{res_folder}/{img}.png"):
                image = Image.open(f"img/cropped/{img}.png")
                image = scale_to_size(image)
                image.save(f"img/scaled/{res_folder}/{img}.png")
            imgs.append((Image.open(f"img/scaled/{res_folder}/{img}.png"), img))
            img_count += 1
        if len(imgs) == capt:
            imgs.pop()
    
    w, h = defs["w_desired"], defs["h_desired"]
    w_s = (w + defs["pad"][1] + defs["pad"][3]) * defs["row_width"]
    h_s = (h + defs["pad"][0] + defs["pad"][2]) * (ceil(len(imgs) / defs["row_width"]))
    section = Image.new("RGBA", (w_s, h_s))
    section.paste(defs["color_mslight"], (0, 0, w_s, h_s))

    ss_colors = [
            defs["color_high1"],
            defs["color_high2"],
    ]
    ss_color = 0
    font = "Starla.ttf"
    line_height = int(defs["pad"][0] * 0.4)
    top_off = defs["pad"][0] // 2 + line_height // 2

    for i, imgname in enumerate(imgs):
        img, name = imgname

        x = defs["pad"][3] + (w + defs["pad"][1] + defs["pad"][3]) * (i % defs["row_width"])
        y = defs["pad"][0] + (h + defs["pad"][0] + defs["pad"][2]) * (i // defs["row_width"])

        if type(img) == str:
            w_buf = (defs["pad"][1] + defs["pad"][3]) * 2
            size, lines = text_to_lines_fit(img, 1, 100, font, (h, w-w_buf))
            offset = (w - size * len(lines)) // 2
            for i, line in enumerate(lines):
                rotation = line.rotate(90, expand=True)
                section.alpha_composite(rotation, (offset+x+size*i, y))
        
            ss_color = (ss_color + 1) % len(ss_colors)
        
            padded_h = h + top_off
            line_c = ImageDraw.Draw(section)
            xpp, ypp = x - defs["pad"][3], y - top_off
            line_c.rectangle((xpp, ypp, xpp+defs["pad"][1]*2, ypp+padded_h), fill=ss_colors[ss_color])
        else:
            text = database[name]["desc"]
            size, lines = text_to_lines_fit(text, 1, 10, "Arkhip_font.ttf", (w, defs["pad"][2]))
            for i, line in enumerate(lines):
                section.alpha_composite(line, (x, y+h+size*i))
            match database[name]["status"]:
                case "have":
                    tint = Image.new("RGBA", img.size, defs["color_have_tint"])
                    img.alpha_composite(tint, (0, 0))
                case "ship":
                    tint = Image.new("RGBA", img.size, defs["color_ship_tint"])
                    img.alpha_composite(tint, (0, 0))
                case "join":
                    tint = Image.new("RGBA", img.size, defs["color_join_tint"])
                    img.alpha_composite(tint, (0, 0))
                case "pay":
                    tint = Image.new("RGBA", img.size, defs["color_pay_tint"])
                    img.alpha_composite(tint, (0, 0))
                case "_":
                    pass
            section.paste(img, (x, y), mask=create_rounded_mask(img.size, defs["w_desired"] // 10))

            # generate a small box in the bottom right of each image
            # which contains the base filename
            if verbose:
                dims = (defs["w_desired"] // 2, defs["h_desired"] // 6)
                id = Image.new("RGBA", dims, defs["color_mdark"])
                id_c = ImageDraw.Draw(id)
                id_c.rectangle((0, 0, dims[0]-1, dims[1]-1), outline=(0, 0, 0), width=2)
                id_text = text_to_lines_fit(name, 1, 100, "Arkhip_font.ttf", (dims[0]-6, dims[1]-6))
                for i, line in enumerate(id_text[1]):
                    id.alpha_composite(line, (3, 3+line.size[1]*i))
                section.alpha_composite(id, (x+w-dims[0]-defs["pad"][1], y+h-dims[1]-defs["pad"][1]))

        side_pad = defs["pad"][1] + defs["pad"][3]
        line_c = ImageDraw.Draw(section)
        xpp, ypp = x - defs["pad"][3], y - top_off
        line_c.rectangle((xpp, ypp, xpp+w+side_pad, ypp+line_height), fill=ss_colors[ss_color])

    return section, img_count

def gen_section_header(section, width):
    global defs

    height = defs["h_desired"] // 2
    header_img = Image.new("RGBA", (width, height), defs["color_mslight"])
    rect = ImageDraw.Draw(header_img)
    radius = defs["w_desired"] // 10
    rect.rounded_rectangle((0, 0, width, height), fill=defs["color_mdark"], radius=radius)
    font = "Catboo.ttf"
    size, lines = text_to_lines_fit(section, 1, 1000, font, (width, height*0.8))
    cmp = Image.new("L", (1, 1))
    cmp = ImageDraw.Draw(cmp)
    fnt = ImageFont.truetype(f"fonts/{font}", size)
    y_offset = (height - size * len(lines)) // 2
    for i, ln in enumerate(lines):
        cmp_len = cmp.textlength(section, fnt)
        line = ln.crop((0, 0, cmp_len, size))
        offset = (width - line.size[0]) // 2
        header_img.alpha_composite(line, (offset, y_offset+size*i))
    return header_img



def gen_sections(sections=None):
    if sections is None:
        sections = set()
        for img in database:
            if database[img]["section"] not in sections:
                sections.add(database[img]["section"])
        sections = list(sections)
    def sort_order(x):
        try:
            return defs["section_order"].index(x)
        except ValueError:
            return 1000
    sections.sort(key=sort_order)
    section_imgs = {section: [gen_section(section)] for section in sections}
    img_count = sum([section_imgs[section][0][1] for section in section_imgs])
    section_imgs = {section: [section_imgs[section][0][0]] for section in sections}
    section_imgs = {section: section_imgs[section] for section in section_imgs if section_imgs[section][0].size[1] > 0}
    if not section_imgs:
        # return an image with the text, "no matches"
        return get_text("no matches", "Arkhip_font.ttf", 100, 100), 0
    width = max([section_imgs[section][0].size[0] for section in section_imgs])
    x_fin, y_fin = width + 50, 0
    for section in section_imgs:
        header = gen_section_header(section, width)
        section_imgs[section].append(header)
        # for header padding
        y_fin += 50
        # for section padding
        y_fin += 20
        # add the actual size
        y_fin += header.size[1] + section_imgs[section][0].size[1]
    final_img = Image.new("RGBA", (x_fin, y_fin), defs["color_mslight"])
    y_offset = 25
    for section in section_imgs:
        section_img, header = section_imgs[section]
        final_img.alpha_composite(header, (25, y_offset))
        y_offset += header.size[1] + 35
        final_img.alpha_composite(section_img, (25, y_offset))
        y_offset += section_img.size[1] + 35
    return final_img, img_count

def gen_header(w, h):
    header = Image.new("RGBA", (w, h), defs["color_mlight"])
    cmp = Image.new("L", (1, 1))
    cmp = ImageDraw.Draw(cmp)

    # zerobaseone
    title = "zerobaseone"
    size = 60
    font = ImageFont.truetype("fonts/ALBAS___.TTF", size)
    cmp_len = int(cmp.textlength(title, font))
    text = Image.new("RGBA", (int(cmp_len + size*0.2), int(size*1.5)), (0, 0, 0, 0))
    txt = ImageDraw.Draw(text)
    txt.text((0, 0), title, fill=(0, 0, 0), font=font)
    header.alpha_composite(text, ((w - text.size[0]) // 2, 15))

    # main header
    title = "SUNG HANBIN"
    size = 150
    font = ImageFont.truetype("fonts/ALBAS___.TTF", size)
    fontu = ImageFont.truetype("fonts/albax.ttf", size)
    cmp_len = int(cmp.textlength(title, font))
    text = Image.new("RGBA", (int(cmp_len + size*0.2), int(size*1.5)), (0, 0, 0, 0))
    txt = ImageDraw.Draw(text)
    txt.text((0, 0), title, fill=defs["color_mdark"], font=fontu)
    y_offset = (h - text.size[1]) // 2 - 10
    header.alpha_composite(text, ((w - text.size[0]) // 2, y_offset))
    txt.text((0, 0), title, fill=(0, 0, 0), font=font)
    y_offset = (h - text.size[1]) // 2 - 10
    header.alpha_composite(text, ((w - text.size[0]) // 2, y_offset))

    # credit
    title = "template by mianbhaos"
    size = 40
    font = ImageFont.truetype("fonts/ALBAS___.TTF", size)
    cmp_len = int(cmp.textlength(title, font))
    text = Image.new("RGBA", (int(cmp_len + size*0.2), int(size*1.5)), (0, 0, 0, 0))
    txt = ImageDraw.Draw(text)
    txt.text((0, 0), title, fill=(0, 0, 0), font=font)
    y_offset = (h - text.size[1]) // 2 + 130
    header.alpha_composite(text, ((w - text.size[0]) // 2, y_offset))

    return header

def gen_template():
    content, img_count = gen_sections()
    sw = defs["w_desired"]
    b_thick = sw // 2
    header_size = defs["h_desired"] * 3
    w, h = content.size
    w_f = w + b_thick*2 + sw*2
    h_f = h + b_thick*2 + sw*2 + header_size
    template = Image.new("RGBA", (w_f, h_f), defs["color_mlight"])
    draw = ImageDraw.Draw(template)
    loc = (sw, header_size+sw, sw*2+w, header_size+sw*2+h)
    draw.rectangle(loc, outline=defs["color_outline"], width=b_thick)
    template.alpha_composite(content, (b_thick+sw, header_size+sw+b_thick))
    header = gen_header(w_f, header_size+sw)
    template.alpha_composite(header, (0, 0))

    # load cute keros
    kero = Image.open("assets/keror.png")
    kero = kero.resize((int(kero.size[0] * 0.5), int(kero.size[1] * 0.5)))
    template.alpha_composite(kero, (w - int(kero.size[0]*0.6), 220))
    kero = Image.open("assets/kerol.png")
    kero = kero.resize((int(kero.size[0] * 0.25), int(kero.size[1] * 0.25)))
    template.alpha_composite(kero, (6, 400))

    template.save("template.png", compress_level=1)

    return img_count

#######
# API #
#######

def template(p_verbose=True):
    global verbose
    verbose = p_verbose

    return gen_template()

def mod(imgs, changes):
    global database

    ret_msgs = []
    for img in imgs:
        if img not in database:
            ret_msgs.append(f"file `{img}` does not exist :c")
            continue

        for change in changes:
            if change not in database[img]:
                ret_msgs.append(f"key `{change}` does not exist :c")
                return ret_msgs

            database[img][change] = changes[change]

    dump_database()
    return ret_msgs

def look(img):
    global database

    if img not in database:
        return f"file `{img}` does not exist :c"
    str_database = ""
    for key in ["status", "desc", "section", "era", "info"]:
        str_database += f"{key}: {database[img][key]}\n\n"
    return f"```-- {img} --\n\n{str_database}```".strip()

def filter(flts):
    global filters

    if not flts:
        filters = {
            "era": "",
            "desc": "",
            "info": "",
            "status": ""
        }

    for flt in flts:
        if flt not in filters:
            continue
        filters[flt] = flts[flt]

if __name__ == "__main__":
    load_prereqs()
    gen_template()


