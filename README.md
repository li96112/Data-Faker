# Data-Faker — 真实感测试数据生成器

> 描述字段，秒出真实数据

## 快速使用

```bash
# 生成 100 条中文用户数据
python3 scripts/faker.py \
  --schema "id, name, email, phone, age:int(18,65), city, company" \
  --count 100 -o users.json

# CSV 格式
python3 scripts/faker.py -s "name, email, phone" -n 1000 -f csv -o data.csv

# SQL INSERT
python3 scripts/faker.py -s "id, name, email" -n 50 -f sql --table users -o seed.sql

# TypeScript mock
python3 scripts/faker.py -s "id, name, avatar, is_active" -n 20 -f ts -o mock.ts
```

## 特色

- **自动推断** — 字段名叫 `email` 就生成邮箱，叫 `phone` 就生成手机号
- **默认中文** — 默认生成中文姓名/地址/手机号/身份证，`--lang en` 可切换英文
- **范围控制** — `age:int(18,65)` 限定范围
- **4 种输出** — JSON / CSV / SQL INSERT / TypeScript
- **真实格式** — 手机号真实前缀、身份证 Luhn 校验、信用卡号有效
- **可复现** — `--seed 42` 固定随机种子

## 支持的字段类型

身份类: id, uuid, name, email, phone, gender, avatar, id_card, credit_card
地理类: address, city, country, zip, latitude, longitude
商业类: company, product, category, price, quantity, status, role
时间类: date, datetime, timestamp, created_at, updated_at
数值类: int(min,max), float(min,max), age, score, rating
文本类: text, paragraph, title, description, comment
布尔类: boolean, is_active, is_verified
技术类: url, ip, mac, color, password, token

## 零依赖

Python 3.9+ 标准库
