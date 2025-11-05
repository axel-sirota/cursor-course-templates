"""
Sample FastAPI Application for Security Testing
This application intentionally contains security vulnerabilities for educational purposes.
"""

from fastapi import FastAPI, HTTPException, Depends, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from typing import Optional, List
import os
import hashlib
import jwt
import json
from datetime import datetime, timedelta

# Initialize FastAPI app
app = FastAPI(title="Vulnerable Blog API", version="1.0.0")

# Database setup (using SQLite for simplicity)
DATABASE_URL = "sqlite:///./vulnerable_blog.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Templates
templates = Jinja2Templates(directory="templates")

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Pydantic models
class User(BaseModel):
    id: Optional[int] = None
    username: str
    email: str
    password: str  # This should be hashed in real apps

class Post(BaseModel):
    id: Optional[int] = None
    title: str
    content: str
    author_id: int
    created_at: Optional[str] = None

class Comment(BaseModel):
    id: Optional[int] = None
    post_id: int
    content: str
    author: str
    created_at: Optional[str] = None

# Database initialization
def init_db():
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                author_id INTEGER NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (author_id) REFERENCES users (id)
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                author TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES posts (id)
            )
        """))
        conn.commit()

# Initialize database
init_db()

# JWT Secret (hardcoded - VULNERABILITY!)
JWT_SECRET = "super-secret-key-123"
JWT_ALGORITHM = "HS256"

# Helper functions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def hash_password(password: str) -> str:
    """Simple hash - VULNERABILITY! Should use bcrypt or similar"""
    return hashlib.md5(password.encode()).hexdigest()

def create_token(user_id: int) -> str:
    """Create JWT token"""
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(token: str) -> Optional[int]:
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload.get("user_id")
    except:
        return None

# Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with potential XSS vulnerability"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/register")
async def register(user: User):
    """User registration - VULNERABILITY: No input validation"""
    db = SessionLocal()
    try:
        # Direct SQL query - VULNERABILITY: SQL Injection possible
        result = db.execute(text(f"""
            INSERT INTO users (username, email, password) 
            VALUES ('{user.username}', '{user.email}', '{hash_password(user.password)}')
        """))
        db.commit()
        return {"message": "User created successfully", "user_id": result.lastrowid}
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()

@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    """User login - VULNERABILITY: SQL Injection possible"""
    db = SessionLocal()
    try:
        # Direct SQL query - VULNERABILITY: SQL Injection possible
        result = db.execute(text(f"""
            SELECT id, username, email FROM users 
            WHERE username = '{username}' AND password = '{hash_password(password)}'
        """)).fetchone()
        
        if result:
            token = create_token(result[0])
            return {"access_token": token, "token_type": "bearer", "user": dict(result._mapping)}
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()

@app.get("/users")
async def get_users():
    """Get all users - VULNERABILITY: No authentication required"""
    db = SessionLocal()
    try:
        result = db.execute(text("SELECT id, username, email FROM users")).fetchall()
        return [dict(row._mapping) for row in result]
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()

@app.post("/posts")
async def create_post(post: Post, request: Request):
    """Create post - VULNERABILITY: No authentication check"""
    db = SessionLocal()
    try:
        # Direct SQL query - VULNERABILITY: SQL Injection possible
        result = db.execute(text(f"""
            INSERT INTO posts (title, content, author_id) 
            VALUES ('{post.title}', '{post.content}', {post.author_id})
        """))
        db.commit()
        return {"message": "Post created successfully", "post_id": result.lastrowid}
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()

@app.get("/posts")
async def get_posts():
    """Get all posts - VULNERABILITY: No authentication required"""
    db = SessionLocal()
    try:
        result = db.execute(text("SELECT * FROM posts ORDER BY created_at DESC")).fetchall()
        return [dict(row._mapping) for row in result]
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()

@app.get("/posts/{post_id}")
async def get_post(post_id: int):
    """Get specific post - VULNERABILITY: SQL Injection possible"""
    db = SessionLocal()
    try:
        # Direct SQL query - VULNERABILITY: SQL Injection possible
        result = db.execute(text(f"SELECT * FROM posts WHERE id = {post_id}")).fetchone()
        if result:
            return dict(result._mapping)
        else:
            raise HTTPException(status_code=404, detail="Post not found")
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()

@app.post("/posts/{post_id}/comments")
async def create_comment(post_id: int, comment: Comment):
    """Create comment - VULNERABILITY: No authentication, SQL Injection possible"""
    db = SessionLocal()
    try:
        # Direct SQL query - VULNERABILITY: SQL Injection possible
        result = db.execute(text(f"""
            INSERT INTO comments (post_id, content, author) 
            VALUES ({post_id}, '{comment.content}', '{comment.author}')
        """))
        db.commit()
        return {"message": "Comment created successfully", "comment_id": result.lastrowid}
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()

@app.get("/posts/{post_id}/comments")
async def get_comments(post_id: int):
    """Get comments for post - VULNERABILITY: SQL Injection possible"""
    db = SessionLocal()
    try:
        # Direct SQL query - VULNERABILITY: SQL Injection possible
        result = db.execute(text(f"SELECT * FROM comments WHERE post_id = {post_id}")).fetchall()
        return [dict(row._mapping) for row in result]
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()

@app.get("/admin")
async def admin_panel():
    """Admin panel - VULNERABILITY: No authentication required"""
    return {"message": "Welcome to admin panel", "users": "Sensitive data here"}

@app.get("/debug")
async def debug_info():
    """Debug endpoint - VULNERABILITY: Exposes sensitive information"""
    return {
        "database_url": DATABASE_URL,
        "jwt_secret": JWT_SECRET,
        "environment": dict(os.environ)
    }

@app.get("/search")
async def search(q: str):
    """Search endpoint - VULNERABILITY: SQL Injection possible"""
    db = SessionLocal()
    try:
        # Direct SQL query - VULNERABILITY: SQL Injection possible
        result = db.execute(text(f"""
            SELECT * FROM posts WHERE title LIKE '%{q}%' OR content LIKE '%{q}%'
        """)).fetchall()
        return [dict(row._mapping) for row in result]
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)