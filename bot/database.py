from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, BigInteger, String, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from paytechuz.integrations.fastapi.models import run_migrations

# Database init
DATABASE_URL = "sqlite:///payments.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    
    telegram_id = Column(BigInteger, primary_key=True)
    full_name = Column(String)
    username = Column(String, nullable=True)
    joined_at = Column(DateTime, default=datetime.utcnow)
    subscription_end_date = Column(DateTime, nullable=True)
    current_plan = Column(String, nullable=True)

    @property
    def is_subscription_active(self):
        if not self.subscription_end_date:
            return False
        return self.subscription_end_date > datetime.utcnow()


class Payment(Base):
    """Business Logic Order/Invoice model (renamed table from 'payments' to 'invoices')"""
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.telegram_id'), nullable=False, index=True)
    amount = Column(Integer, nullable=False)
    payment_method = Column(String(50), nullable=False)
    status = Column(String(50), default="pending")  # pending, paid, cancelled
    tariff = Column(String(50), nullable=True) # basic, standard, premium
    created_at = Column(DateTime, default=datetime.utcnow)
    paid_at = Column(DateTime, nullable=True)
    message_id = Column(BigInteger, nullable=True)
    
    user = relationship("User")


def init_db():
    Base.metadata.create_all(bind=engine)
    # run_migrations yordamida to'lov jadvallarini yaratish
    run_migrations(engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# DB Operations
def get_or_create_user(telegram_id: int, full_name: str, username: str = None) -> User:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        if not user:
            user = User(telegram_id=telegram_id, full_name=full_name, username=username)
            db.add(user)
            db.commit()
            db.refresh(user)
        return user
    finally:
        db.close()

def get_user(telegram_id: int) -> User | None:
    db = SessionLocal()
    try:
        return db.query(User).filter(User.telegram_id == telegram_id).first()
    finally:
        db.close()

def create_payment(user_id: int, amount: int, payment_method: str, tariff: str = None) -> Payment:
    db = SessionLocal()
    try:
        payment = Payment(
            user_id=user_id,
            amount=amount,
            payment_method=payment_method,
            status="pending",
            tariff=tariff
        )
        db.add(payment)
        db.commit()
        db.refresh(payment)
        return payment
    finally:
        db.close()


def get_payment(payment_id: int) -> Payment | None:
    db = SessionLocal()
    try:
        return db.query(Payment).filter(Payment.id == payment_id).first()
    finally:
        db.close()


def activate_subscription(user_id: int, tariff: str):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.telegram_id == user_id).first()
        if user:
            now = datetime.utcnow()
            if user.subscription_end_date and user.subscription_end_date > now:
                start_date = user.subscription_end_date
            else:
                start_date = now
                
            # Define durations
            days = 30 # Default
            if tariff == 'basic':
                days = 30
            elif tariff == 'standard':
                days = 90
            elif tariff == 'premium':
                days = 365
                
            user.subscription_end_date = start_date + timedelta(days=days)
            user.current_plan = tariff
            db.commit()
    finally:
        db.close()


def complete_payment(payment_id: int) -> bool:
    db = SessionLocal()
    try:
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if payment and payment.status == "pending":
            payment.status = "paid"
            payment.paid_at = datetime.utcnow()
            db.commit()
            
            # Activate subscription
            if payment.tariff:
                activate_subscription(payment.user_id, payment.tariff)
                
            return True
        return False
    finally:
        db.close()


def cancel_payment(payment_id: int) -> bool:
    db = SessionLocal()
    try:
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if payment and payment.status == "pending":
            payment.status = "cancelled"
            db.commit()
            return True
        return False
    finally:
        db.close()


def set_payment_message_id(payment_id: int, message_id: int):
    db = SessionLocal()
    try:
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if payment:
            payment.message_id = message_id
            db.commit()
    finally:
        db.close()
