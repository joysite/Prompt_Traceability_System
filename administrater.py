from backend.models import SessionLocal, User, UserRole
from backend.routers.auth import get_password_hash

db = SessionLocal()

username = "admin"
plain_password = "123123"  # 你想设置的管理员密码

# 检查是否已存在同名用户
existing = db.query(User).filter(User.username == username).first()
if existing:
    print("user already exists:", existing.username)
else:
    user = User(
        username=username,
        password_hash=get_password_hash(plain_password),
        role=UserRole.ADMIN,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    print("created admin user:", user.id, user.username)