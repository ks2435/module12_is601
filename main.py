from typing import List

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

from calculation_factory import calculate
from database import Base, engine, get_db
from hashing import hash_password, verify_password
from models import Calculation, User
from schemas import (
    CalculationCreate,
    CalculationRead,
    CalculationUpdate,
    OperationType,
    UserCreate,
    UserLogin,
    UserRead,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Module 12 - Users + Calculations API",
    description="FastAPI backend with user auth and calculation BREAD endpoints.",
    version="1.0.0",
)


@app.get("/", tags=["root"])
def root():
    return {"message": "Module 12 API is running", "docs": "/docs"}


# ---------- Users ----------
@app.post(
    "/users/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    tags=["users"],
)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing = (
        db.query(User)
        .filter((User.username == user.username) | (User.email == user.email))
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already exists")

    new_user = User(
        username=user.username,
        email=user.email,
        password_hash=hash_password(user.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.post("/users/login", response_model=UserRead, tags=["users"])
def login_user(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == credentials.username).first()
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return user


# ---------- Calculations (BREAD) ----------
@app.get("/calculations", response_model=List[CalculationRead], tags=["calculations"])
def browse_calculations(db: Session = Depends(get_db)):
    return db.query(Calculation).order_by(Calculation.id.desc()).all()


@app.get(
    "/calculations/{calc_id}",
    response_model=CalculationRead,
    tags=["calculations"],
)
def read_calculation(calc_id: int, db: Session = Depends(get_db)):
    calc = db.query(Calculation).filter(Calculation.id == calc_id).first()
    if not calc:
        raise HTTPException(status_code=404, detail="Calculation not found")
    return calc


@app.post(
    "/calculations",
    response_model=CalculationRead,
    status_code=status.HTTP_201_CREATED,
    tags=["calculations"],
)
def add_calculation(payload: CalculationCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        result = calculate(payload.a, payload.b, payload.type)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    calc = Calculation(
        a=payload.a,
        b=payload.b,
        type=payload.type.value,
        result=result,
        user_id=payload.user_id,
    )
    db.add(calc)
    db.commit()
    db.refresh(calc)
    return calc


@app.put(
    "/calculations/{calc_id}",
    response_model=CalculationRead,
    tags=["calculations"],
)
def edit_calculation(
    calc_id: int, payload: CalculationUpdate, db: Session = Depends(get_db)
):
    calc = db.query(Calculation).filter(Calculation.id == calc_id).first()
    if not calc:
        raise HTTPException(status_code=404, detail="Calculation not found")

    new_a = payload.a if payload.a is not None else calc.a
    new_b = payload.b if payload.b is not None else calc.b
    new_type_value = payload.type.value if payload.type is not None else calc.type
    new_type_enum = OperationType(new_type_value)

    try:
        new_result = calculate(new_a, new_b, new_type_enum)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    calc.a = new_a
    calc.b = new_b
    calc.type = new_type_value
    calc.result = new_result

    db.commit()
    db.refresh(calc)
    return calc


@app.delete(
    "/calculations/{calc_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["calculations"],
)
def delete_calculation(calc_id: int, db: Session = Depends(get_db)):
    calc = db.query(Calculation).filter(Calculation.id == calc_id).first()
    if not calc:
        raise HTTPException(status_code=404, detail="Calculation not found")
    db.delete(calc)
    db.commit()