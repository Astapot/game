import os
from sqlalchemy.orm import sessionmaker, DeclarativeBase, mapped_column, Mapped
from sqlalchemy import create_engine, String, func, DateTime
import datetime
import psycopg2

POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', '1')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'game')
POSTGRES_HOST = os.getenv('POSTGRES_HOST', '127.0.0.1')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')

#
PG_DSN = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'

# PG_DSN = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@localhost/{POSTGRES_DB}'

engine = create_engine(PG_DSN)
Session = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


class Users(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    password: Mapped[str] = mapped_column(String(), nullable=False)
    date_of_creation: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())
    token: Mapped[str] = mapped_column(String(100), nullable=True)

    @property
    def dict(self):
        return {
            'id': self.id,
            'login': self.login,
            'password': self.password,
            'date_of_creation': self.date_of_creation.isoformat(),
            'token': self.token
        }

    @classmethod
    def get_user(cls, user_id):
        try:
            conn = psycopg2.connect(host=POSTGRES_HOST, user=POSTGRES_USER, password=POSTGRES_PASSWORD, dbname=POSTGRES_DB)
            cur = conn.cursor()
            cur.execute(f"SELECT * FROM Users WHERE id = {user_id} LIMIT 1")
            user = cur.fetchone()
            conn.close()
            if not user:
                return False
            return user
        except Exception as e:
            print(e)
            return False

    @classmethod
    def get_user_by_login(cls, login):
        try:
            with psycopg2.connect(database=POSTGRES_DB, user=POSTGRES_USER, password=POSTGRES_PASSWORD) as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                                   SELECT id
                                   FROM users
                                   WHERE login = %s
                                   LIMIT 1;
                    """, (login,))
                    user_id = cur.fetchone()
                    if user_id:
                        return user_id[0]
                    return False
        except Exception as e:
            print(e)
            return False


Base.metadata.create_all(bind=engine)
