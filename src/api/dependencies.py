from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from src.db.session import SessionLocal
from src.crud.auth_crud import get_user
from src.core.config import JWT_SECRET_KEY, ALGORITHM
from fastapi import Request, Query

# Swagger sẽ hiển thị form login dựa vào tokenUrl này
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def _cred_exc():
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # DEBUG: kiểm tra nhanh format header đã đúng chưa (Bearer <token>)
    if not token or not isinstance(token, str):
        raise _cred_exc()

    try:
        # Nếu có dùng audience/issuer thì thêm verify_* tương ứng
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM], options={"verify_aud": False})
        username: str | None = payload.get("sub")
        if not username:
            # token thiếu claim sub
            raise _cred_exc()
    except JWTError:
        # token hỏng / signature sai / secret khác
        raise _cred_exc()

    user = get_user(db, username)
    if not user:
        raise _cred_exc()
    return user

def require_roles(*allowed: str):
    def _dep(current_user = Depends(get_current_user)):
        have = {getattr(r, "role_name", r) for r in getattr(current_user, "roles", [])}
        if not have.intersection(set(allowed)):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        return current_user
    return _dep

def get_lang(request: Request, lang: str | None = Query(None)) -> str:
    """
    Lấy ngôn ngữ từ query ?lang= hoặc header X-Gen-Lang.
    Chuẩn hoá về 'en' | 'vi' (mặc định 'vi').
    """
    h = request.headers.get("X-Gen-Lang")
    raw = (lang or h or "").strip().lower()
    if raw in ("en", "en-us", "english"):
        return "en"
    if raw in ("vi", "vn", "vi-vn", "vietnamese", "tiếng việt"):
        return "vi"
    return "vi"