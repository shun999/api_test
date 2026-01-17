from fastapi import FastAPI, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# --- データベースの設定 ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./survey.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- データベースのテーブル定義 (Model) ---
class SurveyDB(Base):
    __tablename__ = "surveys"
    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String)
    age = Column(Integer)
    feedback = Column(String)
    rating = Column(Integer)

# データベースのテーブルを作成
Base.metadata.create_all(bind=engine)

# --- FastAPIの型定義 (Pydantic) ---
class SurveyResponse(BaseModel):
    user_name: str
    age: int
    feedback: str
    rating: int

    class Config:
        from_attributes = True

# --- アプリケーション本体 ---
app = FastAPI()

# データベースセッションを取得するための関数
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def read_index():
    return FileResponse("index.html")

# アンケート投稿（DB保存）
@app.post("/submit")
async def submit_survey(response: SurveyResponse, db: Session = Depends(get_db)):
    # DBモデルのインスタンスを作成
    new_data = SurveyDB(
        user_name=response.user_name,
        age=response.age,
        feedback=response.feedback,
        rating=response.rating
    )
    db.add(new_data)
    db.commit()
    db.refresh(new_data)
    return {"message": "データベースに保存しました！", "data": response}

# 結果一覧（DBから取得）
@app.get("/results", response_model=List[SurveyResponse])
async def get_results(db: Session = Depends(get_db)):
    return db.query(SurveyDB).all()