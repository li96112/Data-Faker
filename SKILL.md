---
name: data-faker
description: Generate realistic test data from schema descriptions. Supports Chinese/English names, phones, addresses, ID cards. Output as JSON, CSV, SQL INSERT, or TypeScript mock. Auto-detects field types from names.
metadata: {"openclaw":{"emoji":"🎲","requires":{"bins":["python3"]},"homepage":"https://github.com/li96112/Data-Faker"}}
---

# Data-Faker — 真实感测试数据生成器

> 描述数据模型，秒出百万条真实数据

用自然语言描述字段，默认生成中文真实感测试数据。支持 JSON/CSV/SQL/TypeScript 输出，`--lang en` 可切换英文。

## Agent 调用方式

```bash
# 简单模式：用逗号分隔字段
python3 {baseDir}/scripts/faker.py \
  --schema "id, name, email, phone, age:int(18,65), city, status" \
  --count 100 --format json -o /tmp/fake_data.json

# CSV 输出
python3 {baseDir}/scripts/faker.py \
  --schema "name, email, phone, company, role" \
  --count 1000 --format csv -o /tmp/users.csv

# SQL INSERT 语句
python3 {baseDir}/scripts/faker.py \
  --schema "id, name, email, created_at" \
  --count 50 --format sql --table users -o /tmp/seed.sql

# TypeScript mock 数据
python3 {baseDir}/scripts/faker.py \
  --schema "id, name, email, avatar, is_active" \
  --count 20 --format ts -o /tmp/mock.ts

# 从 JSON schema 文件生成
python3 {baseDir}/scripts/faker.py --schema schema.json --count 500 -o data.json
```

### 触发关键词
- "生成测试数据" / "假数据" / "mock 数据"
- "Data-Faker" / "faker"
- "生成 100 条用户数据" / "造数据"
- "SQL 种子数据" / "CSV 测试数据"

## 字段类型

自动从字段名推断类型，也可以手动指定 `name:type(args)`：

| 类型 | 示例值 | 字段名自动匹配 |
|------|--------|---------------|
| id | 1, 2, 3... | id, *_id |
| uuid | 550e8400-e29b... | uuid |
| name | 王伟 / John Smith | name, full_name |
| email | john@gmail.com | email |
| phone | 13812345678 | phone, mobile, tel |
| address | 北京市朝阳区... | address |
| city | 深圳市 / New York | city |
| company | 字节跳动 | company |
| date | 2026-01-15 | date |
| datetime | 2026-01-15T08:30:00Z | datetime, *_at |
| int(min,max) | 42 | age, quantity |
| float(min,max) | 99.99 | price, score |
| boolean | true/false | is_*, has_*, bool |
| url | https://example.com/... | url, link |
| status | active/pending/... | status |
| role | admin/user/... | role |
| text | Lorem ipsum... | text, content, body |
| id_card | 110101199001011234 | id_card (中国身份证) |
| credit_card | 4532015112830366 | credit_card (Luhn 有效) |

## 零依赖

纯 Python 标准库。

## 文件说明

| 文件 | 作用 |
|------|------|
| `scripts/faker.py` | 核心引擎：数据池 + 生成器 + Schema 解析 + 多格式输出 |
