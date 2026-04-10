# ไฟล์หลักสำหรับรัน API
from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from backend.database import SessionLocal, engine
from backend import models
from datetime import datetime, timedelta
import random
from pydantic import BaseModel
from google.oauth2 import id_token
from google.auth.transport import requests as grequests
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
GOOGLE_CLIENT_ID = "1068833761616-mo5od6pg4fqvt9nq3qdjteqp3fb5qjg3.apps.googleusercontent.com"

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/image", StaticFiles(directory="image"), name="image")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── Pydantic Models ──────────────────────────────────────────
class GoogleTokenRequest(BaseModel):
    token: str

class PhoneRequest(BaseModel):
    phone: str

class OTPVerifyRequest(BaseModel):
    phone: str
    otp_code: str

class ReservationRequest(BaseModel):
    customer_id:      int
    table_number:     str
    occasion:         str = None
    special_requests: str = None
    reservation_date: str
    reservation_time: str
    guest_count:      int = 2
    phone:            str = None   # ← เบอร์โทรลูกค้า

class RegisterRequest(BaseModel):
    username: str
    password: str
    role: str = "customer"

class EmailLoginRequest(BaseModel):
    email: str
    password: str

class RestaurantLoginRequest(BaseModel):
    username: str
    password: str

class StatusUpdateRequest(BaseModel):
    status: str


# ── Auth ─────────────────────────────────────────────────────
@app.post("/auth/send-otp")
def send_otp(req: PhoneRequest, db: Session = Depends(get_db)):
    code = str(random.randint(100000, 999999))
    session = models.OTPSession(
        phone=req.phone,
        otp_code=code,
        expires_at=datetime.utcnow() + timedelta(minutes=5)
    )
    db.add(session)
    db.commit()
    print(f"[OTP] {req.phone} → {code}")
    return {"message": "OTP sent", "dev_otp": code}


@app.post("/auth/verify-otp")
def verify_otp(req: OTPVerifyRequest, db: Session = Depends(get_db)):
    record = db.query(models.OTPSession).filter(
        models.OTPSession.phone      == req.phone,
        models.OTPSession.otp_code   == req.otp_code,
        models.OTPSession.is_used    == False,
        models.OTPSession.expires_at > datetime.utcnow()
    ).first()
    if not record:
        raise HTTPException(status_code=400, detail="OTP ไม่ถูกต้องหรือหมดอายุ")
    record.is_used = True
    db.commit()
    customer = db.query(models.Customer).filter(models.Customer.phone == req.phone).first()
    if not customer:
        customer = models.Customer(name=req.phone, phone=req.phone)
        db.add(customer)
        db.commit()
        db.refresh(customer)
    return {"message": "ยืนยันสำเร็จ", "customer_id": customer.id, "phone": req.phone}


@app.post("/auth/google")
def google_login(req: GoogleTokenRequest, db: Session = Depends(get_db)):
    info     = id_token.verify_oauth2_token(req.token, grequests.Request(), GOOGLE_CLIENT_ID)
    email    = info["email"]
    name     = info.get("name", email)
    customer = db.query(models.Customer).filter(models.Customer.phone == email).first()
    if not customer:
        customer = models.Customer(name=name, phone=email)
        db.add(customer)
        db.commit()
        db.refresh(customer)
    return {"customer_id": customer.id, "phone": email}


@app.post("/auth/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.username == req.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="username นี้ถูกใช้งานแล้ว")
    hashed = pwd_context.hash(req.password[:72])
    user   = models.User(username=req.username, password=hashed, role=req.role)
    db.add(user)
    db.commit()
    db.refresh(user)
    new_customer = models.Customer(id=user.id, name=user.username, phone="000-000-0000")
    db.add(new_customer)
    db.commit()
    return {"customer_id": user.id, "name": user.username, "email": user.username, "role": user.role}


@app.post("/auth/email-login")
def email_login(req: EmailLoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == req.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="ไม่พบบัญชีนี้")
    if not pwd_context.verify(req.password[:72], user.password):
        raise HTTPException(status_code=401, detail="รหัสผ่านไม่ถูกต้อง")
    return {"customer_id": user.id, "name": user.username, "email": user.username, "role": user.role}


@app.post("/auth/restaurant-login")
def restaurant_login(req: RestaurantLoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == req.username).first()
    if not user:
        raise HTTPException(status_code=401, detail="ไม่พบบัญชีนี้")
    if user.role != "restaurant":
        raise HTTPException(status_code=403, detail="บัญชีนี้ไม่ใช่ role ร้านอาหาร")
    if not pwd_context.verify(req.password[:72], user.password):
        raise HTTPException(status_code=401, detail="รหัสผ่านไม่ถูกต้อง")
    return {"customer_id": user.id, "name": user.username, "email": user.username, "role": user.role}


# ── Tables ───────────────────────────────────────────────────
@app.get("/")
def read_root():
    return {"message": "Server is running!"}

@app.get("/tables")
def get_all_tables(db: Session = Depends(get_db)):
    return db.query(models.RestaurantTable).all()

@app.get("/tables/filter")
def filter_tables(zone: str = None, guest_count: int = 1, db: Session = Depends(get_db)):
    query = db.query(models.RestaurantTable).filter(
        # models.RestaurantTable.status    == "available",
        models.RestaurantTable.capacity  >= guest_count
    )
    if zone and zone != "all":
        query = query.filter(models.RestaurantTable.zone == zone)
    return query.all()


# ── Reservations ─────────────────────────────────────────────
@app.post("/reservations")
def create_reservation(req: ReservationRequest, db: Session = Depends(get_db)):
    # ตรวจสอบโต๊ะ
    table = db.query(models.RestaurantTable).filter(
        models.RestaurantTable.table_number == req.table_number
    ).first()
    if not table:
        raise HTTPException(status_code=404, detail="ไม่พบโต๊ะ")

    # ✅ ตรวจสอบจำนวนคนไม่เกิน capacity ของโต๊ะ
    if req.guest_count > table.capacity:
        raise HTTPException(
            status_code=400,
            detail=f"โต๊ะ {req.table_number} รับได้สูงสุด {table.capacity} ท่าน (ขอมา {req.guest_count} ท่าน)"
        )

    # ดึงหรือสร้าง customer
    customer = db.query(models.Customer).filter(models.Customer.id == req.customer_id).first()
    if not customer:
        user = db.query(models.User).filter(models.User.id == req.customer_id).first()
        customer = models.Customer(
            id=req.customer_id,
            name=user.username if user else "Customer",
            phone=req.phone or "000-000-0000"
        )
        db.add(customer)
        db.flush()
    else:
        if req.phone:
            customer.phone = req.phone   # ← อัปเดตเบอร์ในตาราง customers ด้วย

    dt = datetime.strptime(
        f"{req.reservation_date} {req.reservation_time}", "%Y-%m-%d %H:%M"
    )
    reservation = models.Reservation(
        table_id=table.id,
        customer_id=req.customer_id,
        guest_count=req.guest_count,
        phone=req.phone or "",          # ← เก็บเบอร์ใน reservations ด้วย
        reservation_time=dt,
        occasion=req.occasion,
        special_requests=req.special_requests,
        status="pending"
    )
    table.status = "reserved"
    db.add(reservation)
    db.commit()
    return {"message": "จองสำเร็จ", "reservation_id": reservation.id}


@app.get("/reservations/all")
def get_all_reservations(db: Session = Depends(get_db)):
    """ดึงรายการจองทั้งหมด พร้อม username ลูกค้าและเบอร์โทร"""
    reservations = db.query(models.Reservation).all()
    result = []
    for r in reservations:
        # ดึงโต๊ะ
        table = db.query(models.RestaurantTable).filter(
            models.RestaurantTable.id == r.table_id
        ).first()
        # ดึง username จากตาราง users (ตรงกับ customer_id)
        user = db.query(models.User).filter(models.User.id == r.customer_id).first()
        customer_name = user.username if user else f"ลูกค้า #{r.customer_id}"

        # เบอร์โทร: ดึงจาก reservation ก่อน ถ้าไม่มีค่อยดึงจาก customers
        phone_val = getattr(r, "phone", None)
        if not phone_val:
            cust = db.query(models.Customer).filter(
                models.Customer.id == r.customer_id
            ).first()
            phone_val = cust.phone if cust else "-"

        result.append({
            "id":               r.id,
            "table_number":     table.table_number if table else "-",
            "table_capacity":   table.capacity if table else None,
            "customer_id":      r.customer_id,
            "customer_name":    customer_name,          # ← username ลูกค้า
            "guest_count":      r.guest_count,
            "phone":            phone_val,               # ← เบอร์โทร
            "reservation_time": r.reservation_time.isoformat() if r.reservation_time else None,
            "status":           r.status,
            "occasion":         r.occasion,
            "special_requests": r.special_requests,
        })
    return result


@app.get("/reservations/customer/{customer_id}")
def get_customer_reservations(customer_id: int, db: Session = Depends(get_db)):
    reservations = db.query(models.Reservation).filter(
        models.Reservation.customer_id == customer_id
    ).order_by(models.Reservation.reservation_time.desc()).all()

    result = []
    for r in reservations:
        table = db.query(models.RestaurantTable).filter(
            models.RestaurantTable.id == r.table_id
        ).first()
        phone_val = getattr(r, "phone", None)
        if not phone_val:
            cust = db.query(models.Customer).filter(
                models.Customer.id == r.customer_id
            ).first()
            phone_val = cust.phone if cust else "-"

        result.append({
            "id":               r.id,
            "table_number":     table.table_number if table else "-",
            "table_capacity":   table.capacity if table else None,
            "customer_id":      r.customer_id,
            "guest_count":      r.guest_count,
            "phone":            phone_val,
            "reservation_time": r.reservation_time.isoformat() if r.reservation_time else None,
            "status":           r.status,
            "occasion":         r.occasion,
            "special_requests": r.special_requests,
        })
    return result


@app.patch("/reservations/{reservation_id}/status")
def update_reservation_status(
    reservation_id: int,
    req: StatusUpdateRequest,
    db: Session = Depends(get_db)
):
    reservation = db.query(models.Reservation).filter(
        models.Reservation.id == reservation_id
    ).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="ไม่พบการจองนี้")
    reservation.status = req.status
    if req.status == "cancelled":
        table = db.query(models.RestaurantTable).filter(
            models.RestaurantTable.id == reservation.table_id
        ).first()
        if table:
            table.status = "available"
    db.commit()
    return {"message": "อัปเดตสถานะสำเร็จ", "status": req.status}


@app.post("/reservations/{reservation_id}/cancel")
def cancel_reservation(reservation_id: int, db: Session = Depends(get_db)):
    reservation = db.query(models.Reservation).filter(
        models.Reservation.id == reservation_id
    ).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="ไม่พบรายการจอง")
    reservation.status = "cancelled"
    table = db.query(models.RestaurantTable).filter(
        models.RestaurantTable.id == reservation.table_id
    ).first()
    if table:
        table.status = "available"
    db.commit()
    return {"message": "ยกเลิกการจองเรียบร้อยแล้ว"}


# ── Seed ─────────────────────────────────────────────────────
@app.on_event("startup")
def seed_restaurant():
    db = SessionLocal()
    existing = db.query(models.User).filter(models.User.username == "restaurant").first()
    if not existing:
        hashed = pwd_context.hash("restaurant1234"[:72])
        owner  = models.User(username="restaurant", password=hashed, role="restaurant")
        db.add(owner)
        db.commit()
    db.close()