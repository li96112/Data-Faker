#!/usr/bin/env python3
"""Data-Faker: Generate realistic test data from schema descriptions.

Supports: JSON, CSV, SQL INSERT, Python dict, TypeScript mock.
Features: Chinese/English names, real-format phones/emails/addresses/IDs,
           relational data (foreign keys), custom rules, large-scale generation.
"""

import argparse
import csv
import io
import json
import math
import os
import random
import re
import string
import sys
import uuid
from datetime import datetime, timedelta, timezone


# ---------------------------------------------------------------------------
# Data pools — realistic Chinese + English data
# ---------------------------------------------------------------------------

FIRST_NAMES_EN = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael",
    "Linda", "William", "Elizabeth", "David", "Barbara", "Richard", "Susan",
    "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen", "Daniel",
    "Emma", "Oliver", "Ava", "Liam", "Sophia", "Noah", "Isabella",
]
LAST_NAMES_EN = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Rodriguez", "Martinez", "Anderson", "Taylor", "Thomas",
    "Jackson", "White", "Harris", "Martin", "Thompson", "Moore", "Clark",
]

FIRST_NAMES_ZH = [
    "伟", "芳", "娜", "秀英", "敏", "静", "丽", "强", "磊", "洋",
    "勇", "艳", "杰", "娟", "涛", "明", "超", "秀兰", "霞", "平",
    "刚", "桂英", "华", "飞", "玉兰", "萍", "红", "军", "兰", "民",
]
LAST_NAMES_ZH = [
    "王", "李", "张", "刘", "陈", "杨", "黄", "赵", "周", "吴",
    "徐", "孙", "马", "胡", "朱", "郭", "何", "林", "罗", "高",
]

CITIES_ZH = [
    "北京市", "上海市", "广州市", "深圳市", "杭州市", "成都市", "武汉市",
    "南京市", "重庆市", "西安市", "苏州市", "天津市", "长沙市", "郑州市",
    "青岛市", "大连市", "厦门市", "宁波市", "合肥市", "福州市",
]
DISTRICTS_ZH = [
    "朝阳区", "海淀区", "浦东新区", "南山区", "西湖区", "武侯区",
    "江汉区", "鼓楼区", "渝中区", "雁塔区", "姑苏区", "和平区",
]
STREETS_ZH = [
    "中关村大街", "南京路", "解放路", "人民路", "建设路", "长安街",
    "和平路", "文化路", "科技路", "创业路", "幸福路", "新华路",
]

CITIES_EN = [
    "New York", "Los Angeles", "Chicago", "Houston", "Phoenix",
    "San Francisco", "Seattle", "Boston", "Denver", "Austin",
    "Portland", "Miami", "Atlanta", "Dallas", "San Diego",
]
STATES_EN = [
    "CA", "NY", "TX", "FL", "IL", "WA", "MA", "CO", "AZ", "GA",
]

COMPANIES = [
    "Acme Corp", "Globex", "Initech", "Umbrella Corp", "Stark Industries",
    "Wayne Enterprises", "Cyberdyne", "Aperture Science", "Massive Dynamic",
    "Soylent Corp", "Weyland-Yutani", "Oscorp", "LexCorp", "Pied Piper",
]
COMPANIES_ZH = [
    "华为技术有限公司", "阿里巴巴集团", "腾讯科技", "字节跳动",
    "百度在线", "京东集团", "美团科技", "小米科技", "网易",
    "滴滴出行", "快手科技", "拼多多", "蚂蚁集团", "哔哩哔哩",
]

DOMAINS = ["gmail.com", "outlook.com", "yahoo.com", "hotmail.com", "icloud.com",
           "163.com", "qq.com", "126.com", "sina.com"]

LOREM_WORDS = (
    "lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod "
    "tempor incididunt ut labore et dolore magna aliqua enim ad minim veniam "
    "quis nostrud exercitation ullamco laboris nisi aliquip ex ea commodo "
    "consequat duis aute irure in reprehenderit voluptate velit esse cillum "
    "fugiat nulla pariatur excepteur sint occaecat cupidatat non proident "
    "sunt culpa qui officia deserunt mollit anim id est laborum"
).split()

PRODUCT_ADJECTIVES = ["Premium", "Ultra", "Pro", "Essential", "Classic", "Smart", "Elite"]
PRODUCT_NOUNS = ["Widget", "Gadget", "Device", "Tool", "Module", "System", "Kit", "Pack"]
COLORS = ["Red", "Blue", "Green", "Black", "White", "Silver", "Gold", "Purple"]
CATEGORIES = ["Electronics", "Clothing", "Food", "Books", "Sports", "Home", "Beauty", "Toys"]


# ---------------------------------------------------------------------------
# Generator functions
# ---------------------------------------------------------------------------

def gen_id(counter=[0]):
    counter[0] += 1
    return counter[0]


def gen_uuid():
    return str(uuid.uuid4())


def gen_name(lang="en"):
    if lang == "zh":
        return random.choice(LAST_NAMES_ZH) + random.choice(FIRST_NAMES_ZH)
    return f"{random.choice(FIRST_NAMES_EN)} {random.choice(LAST_NAMES_EN)}"


def gen_first_name(lang="en"):
    return random.choice(FIRST_NAMES_ZH if lang == "zh" else FIRST_NAMES_EN)


def gen_last_name(lang="en"):
    return random.choice(LAST_NAMES_ZH if lang == "zh" else LAST_NAMES_EN)


def gen_email(name=None):
    if name:
        local = name.lower().replace(" ", ".").replace("·", "")
    else:
        local = random.choice(FIRST_NAMES_EN).lower() + str(random.randint(1, 999))
    return f"{local}@{random.choice(DOMAINS)}"


def gen_phone(lang="en"):
    if lang == "zh":
        prefixes = ["130", "131", "132", "133", "135", "136", "137", "138", "139",
                     "150", "151", "152", "153", "155", "156", "157", "158", "159",
                     "170", "176", "177", "178", "180", "181", "182", "183", "186", "187", "188", "189"]
        return random.choice(prefixes) + "".join(str(random.randint(0, 9)) for _ in range(8))
    return f"+1{random.randint(200, 999)}{random.randint(200, 999)}{random.randint(1000, 9999)}"


def gen_address(lang="en"):
    if lang == "zh":
        return f"{random.choice(CITIES_ZH)}{random.choice(DISTRICTS_ZH)}{random.choice(STREETS_ZH)}{random.randint(1, 200)}号"
    return f"{random.randint(1, 9999)} {random.choice(['Main', 'Oak', 'Pine', 'Elm', 'Maple', 'Cedar'])} {'St' if random.random() > 0.5 else 'Ave'}, {random.choice(CITIES_EN)}, {random.choice(STATES_EN)} {random.randint(10000, 99999)}"


def gen_city(lang="en"):
    return random.choice(CITIES_ZH if lang == "zh" else CITIES_EN)


def gen_company(lang="en"):
    return random.choice(COMPANIES_ZH if lang == "zh" else COMPANIES)


def gen_date(start="2020-01-01", end="2026-12-31"):
    s = datetime.strptime(start, "%Y-%m-%d")
    e = datetime.strptime(end, "%Y-%m-%d")
    delta = (e - s).days
    d = s + timedelta(days=random.randint(0, max(delta, 1)))
    return d.strftime("%Y-%m-%d")


def gen_datetime(start="2020-01-01", end="2026-12-31"):
    return gen_date(start, end) + f"T{random.randint(0,23):02d}:{random.randint(0,59):02d}:{random.randint(0,59):02d}Z"


def gen_timestamp():
    return int(datetime(2020, 1, 1).timestamp()) + random.randint(0, 200000000)


def gen_bool():
    return random.choice([True, False])


def gen_int(min_val=0, max_val=1000):
    return random.randint(min_val, max_val)


def gen_float(min_val=0, max_val=1000, decimals=2):
    return round(random.uniform(min_val, max_val), decimals)


def gen_price(min_val=0.99, max_val=9999.99):
    return round(random.uniform(min_val, max_val), 2)


def gen_url(domain=None):
    d = domain or random.choice(["example.com", "test.org", "demo.io", "app.dev"])
    paths = ["products", "users", "api", "docs", "blog", "about"]
    return f"https://{d}/{random.choice(paths)}/{random.randint(1, 9999)}"


def gen_ip():
    return f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"


def gen_mac():
    return ":".join(f"{random.randint(0,255):02x}" for _ in range(6))


def gen_color_hex():
    return f"#{random.randint(0, 0xFFFFFF):06x}"


def gen_lorem(words=10):
    return " ".join(random.choices(LOREM_WORDS, k=words)).capitalize() + "."


def gen_paragraph(sentences=3):
    return " ".join(gen_lorem(random.randint(8, 20)) for _ in range(sentences))


def gen_product_name():
    return f"{random.choice(PRODUCT_ADJECTIVES)} {random.choice(COLORS)} {random.choice(PRODUCT_NOUNS)}"


def gen_category():
    return random.choice(CATEGORIES)


def gen_status():
    return random.choice(["active", "inactive", "pending", "suspended", "deleted"])


def gen_role():
    return random.choice(["admin", "user", "editor", "viewer", "moderator"])


def gen_gender(lang="en"):
    if lang == "zh":
        return random.choice(["男", "女"])
    return random.choice(["male", "female"])


def gen_avatar():
    return f"https://i.pravatar.cc/150?u={uuid.uuid4().hex[:8]}"


def gen_credit_card():
    """Generate Luhn-valid credit card number."""
    prefix = random.choice(["4", "51", "52", "53", "54", "55", "37"])
    remaining = 16 - len(prefix) - 1
    number = prefix + "".join(str(random.randint(0, 9)) for _ in range(remaining))
    # Luhn check digit
    digits = [int(d) for d in number]
    for i in range(len(digits) - 1, -1, -2):
        digits[i] *= 2
        if digits[i] > 9:
            digits[i] -= 9
    check = (10 - sum(digits) % 10) % 10
    return number + str(check)


def gen_id_card_zh():
    """Generate realistic Chinese ID card number (18 digits)."""
    # Area code (Beijing)
    area = random.choice(["110101", "310101", "440305", "330102", "510104"])
    # Birth date
    year = random.randint(1960, 2005)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    birth = f"{year}{month:02d}{day:02d}"
    # Sequence
    seq = f"{random.randint(0, 999):03d}"
    base = area + birth + seq
    # Check digit
    weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
    check_chars = "10X98765432"
    total = sum(int(base[i]) * weights[i] for i in range(17))
    check = check_chars[total % 11]
    return base + check


# ---------------------------------------------------------------------------
# Field type mapping
# ---------------------------------------------------------------------------

FIELD_GENERATORS = {
    # Identity
    "id": lambda lang: gen_id(),
    "uuid": lambda lang: gen_uuid(),
    "name": gen_name,
    "first_name": gen_first_name,
    "last_name": gen_last_name,
    "username": lambda lang: f"user_{random.randint(1000, 99999)}",
    "email": lambda lang: gen_email(),
    "phone": gen_phone,
    "gender": gen_gender,
    "avatar": lambda lang: gen_avatar(),
    "id_card": lambda lang: gen_id_card_zh(),

    # Location
    "address": gen_address,
    "city": gen_city,
    "country": lambda lang: "中国" if lang == "zh" else random.choice(["US", "UK", "CA", "AU", "DE"]),
    "zip": lambda lang: f"{random.randint(10000, 99999)}",
    "latitude": lambda lang: gen_float(-90, 90, 6),
    "longitude": lambda lang: gen_float(-180, 180, 6),

    # Business
    "company": gen_company,
    "product": lambda lang: gen_product_name(),
    "category": lambda lang: gen_category(),
    "price": lambda lang: gen_price(),
    "quantity": lambda lang: gen_int(1, 100),
    "status": lambda lang: gen_status(),
    "role": lambda lang: gen_role(),

    # Date/Time
    "date": lambda lang: gen_date(),
    "datetime": lambda lang: gen_datetime(),
    "timestamp": lambda lang: gen_timestamp(),
    "created_at": lambda lang: gen_datetime(),
    "updated_at": lambda lang: gen_datetime(),

    # Numbers
    "int": lambda lang: gen_int(),
    "integer": lambda lang: gen_int(),
    "float": lambda lang: gen_float(),
    "number": lambda lang: gen_float(),
    "age": lambda lang: gen_int(18, 80),
    "score": lambda lang: gen_float(0, 100, 1),
    "rating": lambda lang: gen_float(1, 5, 1),
    "percent": lambda lang: gen_float(0, 100, 1),

    # Text
    "text": lambda lang: gen_lorem(15),
    "paragraph": lambda lang: gen_paragraph(),
    "title": lambda lang: gen_lorem(5),
    "description": lambda lang: gen_paragraph(2),
    "bio": lambda lang: gen_paragraph(2),
    "comment": lambda lang: gen_lorem(random.randint(5, 20)),

    # Boolean
    "bool": lambda lang: gen_bool(),
    "boolean": lambda lang: gen_bool(),
    "is_active": lambda lang: gen_bool(),
    "is_verified": lambda lang: gen_bool(),

    # Technical
    "url": lambda lang: gen_url(),
    "ip": lambda lang: gen_ip(),
    "mac": lambda lang: gen_mac(),
    "color": lambda lang: gen_color_hex(),
    "credit_card": lambda lang: gen_credit_card(),
    "password": lambda lang: "".join(random.choices(string.ascii_letters + string.digits + "!@#$%", k=12)),
    "token": lambda lang: uuid.uuid4().hex,
    "hash": lambda lang: uuid.uuid4().hex + uuid.uuid4().hex[:32],
}

# Auto-detect field type from field name
FIELD_NAME_HINTS = [
    (r"(?:^id$|_id$)", "id"),
    (r"uuid", "uuid"),
    (r"(?:^name$|full.?name)", "name"),
    (r"first.?name", "first_name"),
    (r"last.?name", "last_name"),
    (r"user.?name", "username"),
    (r"id.?card", "id_card"),
    (r"credit.?card", "credit_card"),
    (r"e.?mail", "email"),
    (r"phone|mobile|tel", "phone"),
    (r"avatar|photo|image", "avatar"),
    (r"address|addr", "address"),
    (r"city", "city"),
    (r"country", "country"),
    (r"zip|postal", "zip"),
    (r"lat(?:itude)?$", "latitude"),
    (r"lng|lon(?:gitude)?$", "longitude"),
    (r"company|org", "company"),
    (r"product", "product"),
    (r"category|cat", "category"),
    (r"price|cost|amount", "price"),
    (r"quantity|qty|count", "quantity"),
    (r"status", "status"),
    (r"role", "role"),
    (r"gender|sex", "gender"),
    (r"age", "age"),
    (r"score", "score"),
    (r"rating", "rating"),
    (r"date|_at$", "datetime"),
    (r"created", "created_at"),
    (r"updated|modified", "updated_at"),
    (r"title", "title"),
    (r"desc(?:ription)?", "description"),
    (r"bio", "bio"),
    (r"comment|note|remark", "comment"),
    (r"text|content|body", "text"),
    (r"url|link|href", "url"),
    (r"ip.?addr", "ip"),
    (r"color", "color"),
    (r"password|passwd|pwd", "password"),
    (r"token", "token"),
    (r"bool|is_|has_|can_", "boolean"),
]


def detect_field_type(field_name):
    """Auto-detect generator from field name."""
    lower = field_name.lower()
    for pattern, ftype in FIELD_NAME_HINTS:
        if re.search(pattern, lower):
            return ftype
    return "text"  # Default fallback


# ---------------------------------------------------------------------------
# Schema parser
# ---------------------------------------------------------------------------

def parse_schema(schema_input):
    """Parse various schema formats into a list of field definitions.

    Supports:
    - Simple: "name, email, phone, age:int, price:float"
    - JSON Schema: {"fields": [{"name": "id", "type": "int"}, ...]}
    - TypeScript-like: "{ id: number; name: string; email: string; }"
    - SQL-like: "id INT, name VARCHAR, email VARCHAR, age INT"
    """
    if isinstance(schema_input, dict):
        # JSON schema format
        fields = []
        for f in schema_input.get("fields", []):
            if isinstance(f, dict):
                fields.append({
                    "name": f["name"],
                    "type": f.get("type", detect_field_type(f["name"])),
                    "options": f.get("options", {}),
                })
            elif isinstance(f, str):
                fields.append(parse_field_str(f))
        return fields

    if isinstance(schema_input, list):
        return [parse_field_str(f) if isinstance(f, str) else f for f in schema_input]

    # String format
    text = schema_input.strip()

    # Remove TypeScript-like braces
    text = re.sub(r'^{|}$', '', text).strip()

    # Split by comma or semicolon, but not commas inside parentheses
    parts = re.split(r'[;,]\s*(?![^()]*\))', text)
    return [parse_field_str(p.strip()) for p in parts if p.strip()]


def parse_field_str(field_str):
    """Parse a single field string like 'name:string' or 'age:int(18,80)'."""
    field_str = field_str.strip()

    # Format: name:type or name:type(args) or just name
    m = re.match(r'^(\w+)\s*[:\s]\s*(\w+)(?:\(([^)]*)\))?\s*$', field_str)
    if m:
        name = m.group(1)
        ftype = m.group(2).lower()
        args = m.group(3)

        options = {}
        if args:
            positional = []
            for arg in args.split(","):
                arg = arg.strip()
                if "=" in arg:
                    k, v = arg.split("=", 1)
                    options[k.strip()] = v.strip()
                else:
                    positional.append(arg)
            # Convert positional args: (min, max) for numeric types
            if len(positional) == 2 and ftype in ("int", "integer", "float", "number", "decimal"):
                options["min"] = positional[0]
                options["max"] = positional[1]
            elif len(positional) == 1 and ftype in ("int", "integer", "float", "number"):
                options["max"] = positional[0]
            elif positional:
                options["args"] = positional

        # Map SQL types
        type_map = {
            "varchar": "text", "char": "text", "string": "text",
            "int": "int", "integer": "int", "bigint": "int",
            "float": "float", "double": "float", "decimal": "price",
            "number": "float", "numeric": "float",
            "bool": "boolean", "boolean": "boolean",
            "date": "date", "datetime": "datetime", "timestamp": "timestamp",
        }
        ftype = type_map.get(ftype, ftype)

        # Auto-detect from name if type is generic
        if ftype in ("text", "string"):
            ftype = detect_field_type(name)

        return {"name": name, "type": ftype, "options": options}

    # Just a name, auto-detect type
    name = field_str.split()[0] if " " in field_str else field_str
    return {"name": name, "type": detect_field_type(name), "options": {}}


# ---------------------------------------------------------------------------
# Data generator
# ---------------------------------------------------------------------------

def generate_records(fields, count=10, lang="zh", seed=None):
    """Generate N records based on field definitions."""
    if seed is not None:
        random.seed(seed)

    # Reset ID counter
    gen_id.__defaults__[0][0] = 0

    records = []
    for _ in range(count):
        record = {}
        for field in fields:
            name = field["name"]
            ftype = field["type"]
            options = field.get("options", {})

            gen = FIELD_GENERATORS.get(ftype)
            if gen:
                value = gen(lang)
            else:
                value = gen_lorem(5)

            # Apply options
            if "min" in options and "max" in options:
                try:
                    min_v = float(options["min"])
                    max_v = float(options["max"])
                    if ftype in ("int", "integer"):
                        value = random.randint(int(min_v), int(max_v))
                    else:
                        value = round(random.uniform(min_v, max_v), 2)
                except:
                    pass

            if "values" in options:
                # Enum values
                value = random.choice(options["values"].split("|"))

            record[name] = value
        records.append(record)

    return records


# ---------------------------------------------------------------------------
# Output formatters
# ---------------------------------------------------------------------------

def to_json(records, indent=2):
    return json.dumps(records, indent=indent, ensure_ascii=False, default=str)


def to_csv(records):
    if not records:
        return ""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=records[0].keys())
    writer.writeheader()
    writer.writerows(records)
    return output.getvalue()


def to_sql(records, table_name="data"):
    if not records:
        return ""
    lines = []
    cols = list(records[0].keys())
    for r in records:
        vals = []
        for c in cols:
            v = r[c]
            if v is None:
                vals.append("NULL")
            elif isinstance(v, bool):
                vals.append("1" if v else "0")
            elif isinstance(v, (int, float)):
                vals.append(str(v))
            else:
                vals.append(f"'{str(v).replace(chr(39), chr(39)+chr(39))}'")
        lines.append(f"INSERT INTO {table_name} ({', '.join(cols)}) VALUES ({', '.join(vals)});")
    return "\n".join(lines)


def to_typescript(records, type_name="Record"):
    if not records:
        return ""
    # Infer types
    fields = {}
    for k, v in records[0].items():
        if isinstance(v, bool):
            fields[k] = "boolean"
        elif isinstance(v, int):
            fields[k] = "number"
        elif isinstance(v, float):
            fields[k] = "number"
        else:
            fields[k] = "string"

    lines = [f"interface {type_name} {{"]
    for k, t in fields.items():
        lines.append(f"  {k}: {t};")
    lines.append("}\n")
    lines.append(f"const mockData: {type_name}[] = {json.dumps(records, indent=2, ensure_ascii=False, default=str)};")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Data-Faker: Generate realistic test data",
        epilog='Example: python3 faker.py --schema "name, email, phone, age:int(18,65)" --count 100 --format json',
    )
    parser.add_argument("--schema", "-s", required=True,
                        help='Field definitions: "name, email, phone, age:int(18,65)" or JSON file path')
    parser.add_argument("--count", "-n", type=int, default=10, help="Number of records (default: 10)")
    parser.add_argument("--format", "-f", default="json",
                        choices=["json", "csv", "sql", "typescript", "ts"],
                        help="Output format (default: json)")
    parser.add_argument("--lang", "-l", default="zh", choices=["en", "zh"],
                        help="Language for names/addresses (default: zh)")
    parser.add_argument("--table", default="data", help="Table name for SQL output")
    parser.add_argument("--seed", type=int, help="Random seed for reproducibility")
    parser.add_argument("--output", "-o", help="Output file path")
    args = parser.parse_args()

    # Parse schema
    schema_input = args.schema
    if os.path.isfile(schema_input):
        with open(schema_input, "r", encoding="utf-8") as f:
            schema_input = json.load(f)

    fields = parse_schema(schema_input)

    if not fields:
        print("[!] No fields parsed from schema", file=sys.stderr)
        sys.exit(1)

    print(f"[*] Schema: {len(fields)} fields — {', '.join(f['name'] + ':' + f['type'] for f in fields)}")
    print(f"[*] Generating {args.count} records ({args.lang})...")

    records = generate_records(fields, args.count, args.lang, args.seed)

    # Format output
    fmt = args.format.lower()
    if fmt == "json":
        output = to_json(records)
    elif fmt == "csv":
        output = to_csv(records)
    elif fmt == "sql":
        output = to_sql(records, args.table)
    elif fmt in ("typescript", "ts"):
        output = to_typescript(records)
    else:
        output = to_json(records)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"[+] Generated {args.count} records → {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
