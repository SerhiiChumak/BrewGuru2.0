import sys
from pathlib import Path
from datetime import datetime, timezone

# 1. Додаємо шлях до кореня проекту, щоб імпорти працювали
sys.path.insert(0, str(Path(__file__).parent))

# Імпортуємо модулі
from database import SessionLocal, engine
import models
import auth


def seed_db():
    print("🌱 Наповнення бази даних тестовими даними...")
    db = SessionLocal()

    try:
        # Створюємо таблиці, якщо їх ще немає
        models.Base.metadata.create_all(bind=engine)

        # 1. Створюємо адміна
        admin_email = "admin@brewguru.com"
        admin = db.query(models.User).filter(models.User.email == admin_email).first()

        if not admin:
            print("  - Створюю адміна...")
            admin = models.User(
                email=admin_email,
                hashed_password=auth.get_password_hash("admin123"),
                first_name="Admin",
                last_name="Brew",
                role="admin"
            )
            db.add(admin)
            db.flush()
        else:
            print(f"  - Адмін {admin_email} вже існує.")

        # 2. Дані для кав'ярень (ті, що дав фронтенд)
        cafes_to_seed = [
            {
                "name": "Coffee Hub",
                "address": "123 Main Street",
                "city": "Kyiv",
                "phone": "+380 44 123 4567",
                "rating": 4.5,
                "average_check": 150,
                "image_url": "https://images.unsplash.com/photo-1509042239860-f550ce710b93",
                "description": "Step into a thoughtfully designed thematic café...",
                "hours": [
                    {"weekday": 1, "open": "08:00", "close": "22:00", "is_open": True},
                    {"weekday": 7, "open": None, "close": None, "is_open": False},
                ],
                "tables": [
                    {"name": "Table 1", "seats": 1},
                    {"name": "Table 2", "seats": 2},
                ]
            },
            {
                "name": "Tea & Talk",
                "address": "45 Green Avenue",
                "city": " Lviv",
                "phone": "+380 32 987 6543",
                "rating": 4.2,
                "average_check": 120,
                "image_url": "https://images.unsplash.com/photo-1556742044-3c52d6e88c62",
                "description": "A cozy and welcoming café designed for meaningful conversations...",
                "hours": [
                    {"weekday": i, "open": "09:00", "close": "21:00", "is_open": True} for i in range(1, 8)
                ],
                "tables": [
                    {"name": "Table 1", "seats": 2},
                ]
            }
        ]

        # 3. Наповнюємо кав'ярні
        for c_data in cafes_to_seed:
            existing_cafe = db.query(models.Cafe).filter(models.Cafe.name == c_data["name"]).first()

            if not existing_cafe:
                print(f"  - Додаю кав'ярню: {c_data['name']}...")
                cafe = models.Cafe(
                    name=c_data["name"],
                    address=c_data["address"],
                    city=c_data["city"],
                    phone=c_data["phone"],
                    rating=c_data["rating"],
                    average_check=c_data["average_check"],
                    image_url=c_data["image_url"],
                    description=c_data["description"]
                )
                db.add(cafe)
                db.flush()

                # Додаємо години (OpeningHours)
                for h in c_data["hours"]:
                    hour = models.OpeningHours(
                        cafe_id=cafe.id,
                        weekday=h["weekday"],
                        open_time=h["open"],
                        close_time=h["close"],
                        is_open=h["is_open"]
                    )
                    db.add(hour)

                # Додаємо столи (Tables)
                for t in c_data["tables"]:
                    table = models.Table(
                        cafe_id=cafe.id,
                        name=t["name"],
                        seats=t["seats"]
                    )
                    db.add(table)
            else:
                print(f"  - Кав'ярня {c_data['name']} вже є в базі.")

        db.commit()
        print("\n✨ Базу успішно оновлено!")

    except Exception as e:
        print(f"\n❌ Помилка: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_db()
