from bs4.element import Tag


def main(): ...


def parse_stacked_cell(td: Tag) -> tuple[str | None, str | None]:
    paragraphs = td.find_all("p")
    values = [p.get_text(strip=True) or None for p in paragraphs]
    while len(values) < 2:
        values.append(None)

    return values[0], values[1]


def parse_label_value_box(box: Tag) -> dict[str, str]:
    result = {}
    list_items = box.find_all("li")
    for item in list_items:
        label_tag = item.find("i")
        if label_tag is None:
            continue
        label = label_tag.get_text(strip=True).rstrip(":")
        value = item.get_text().replace(label_tag.get_text(), "", 1).strip()
        result[label] = value

    return result


def extract_id_from_href(href: str) -> str:
    path_segments = href.rstrip("/").split("/")

    return path_segments[-1]


def parse_fight_metadata(content: Tag) -> dict[str, str]:
    result = {}
    label_tags = content.find_all("i", class_="b-fight-details__label")

    for label_tag in label_tags:
        item = label_tag.parent
        label = label_tag.get_text(strip=True).rstrip(":")
        value = item.get_text().replace(label_tag.get_text(), "", 1).strip()

        if not value:
            value = item.parent.get_text().replace(item.get_text(), "", 1).strip()

        result[label] = value

    return result


if __name__ == "__main__":
    main()
