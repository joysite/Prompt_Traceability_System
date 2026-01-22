from datetime import datetime

from backend.models import SessionLocal, Batch, BatchStatus


def main():
    db = SessionLocal()

    # 1) 根据需要修改批次编号，避免重复
    batch_id = "TEST-20250101"

    # 2) 如果已存在同名批次，直接提示并退出
    existing = db.query(Batch).filter(Batch.batch_id == batch_id).first()
    if existing:
        print(f"batch {batch_id} already exists")
        return

    # 3) 示例数据：可以按需修改
    product_name = "眉山有机柑橘"

    origin_info = {
        "address": "四川省眉山市 XX 生态果园基地",
        "images": [
            "https://example.com/images/origin1.jpg",
            "https://example.com/images/origin2.jpg",
        ],
    }

    process_info = [
        {
            "title": "采摘完成",
            "time": "2025-01-05 09:00",
            "desc": "人工采摘，初步筛选坏果。",
        },
        {
            "title": "分拣预冷",
            "time": "2025-01-05 14:30",
            "desc": "按大小分级，2-8℃ 预冷处理。",
        },
        {
            "title": "包装入箱",
            "time": "2025-01-06 10:00",
            "desc": "使用食品级包装材料密封入箱。",
        },
    ]

    logistics_static = {
        "description": "全程 2-8℃ 冷链运输，统一装箱标准。",
        "route_images": [
            "https://example.com/images/route1.jpg",
        ],
    }

    quality_report = {
        "result": "抽检合格，农残远低于国家标准。",
        "report_images": [
            "https://example.com/images/report1.jpg",
        ],
    }

    batch = Batch(
        batch_id=batch_id,
        product_name=product_name,
        origin_info=json_dumps(origin_info),
        process_info=json_dumps(process_info),
        logistics_static=json_dumps(logistics_static),
        quality_report=json_dumps(quality_report),
        status=BatchStatus.NORMAL,
        scan_count=0,
        created_at=datetime.utcnow(),
    )

    db.add(batch)
    db.commit()
    db.refresh(batch)

    print("created batch:", batch.batch_id, "id:", batch.id)


def json_dumps(obj) -> str:
    import json

    return json.dumps(obj, ensure_ascii=False)


if __name__ == "__main__":
    main()