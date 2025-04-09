from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from analogapi.database import SessionLocal
from analogapi.models.tag import Tag
from analogapi.schemas.tag import TagCreate, TagOut

router = APIRouter(prefix="/tags", tags=["tags"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# CREATE NEW TAG
@router.post("/", response_model=TagOut)
def create_tag(tag: TagCreate, db: Session = Depends(get_db)):
    existing_tag = db.query(Tag).filter(Tag.name == tag.name).first()
    if existing_tag:
        raise HTTPException(status_code=400, detail="Tag already exists")
    
    db_tag = Tag(**tag.model_dump())
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag

# GET ALL TAGS
@router.get("/", response_model=list[TagOut])
def get_all_tags(db: Session = Depends(get_db)):
    tags = db.query(Tag).all()
    return tags

# GET TAG BY ID
@router.get("/{tag_id}", response_model=TagOut)
def get_tag_by_id(tag_id: int, db: Session = Depends(get_db)):
    db_tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if db_tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    return db_tag

# EDIT A TAG
@router.put("/{tag_id}", response_model=TagOut)
def edit_tag(tag_id: int, tag: TagCreate, db: Session = Depends(get_db)):
    db_tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if db_tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    existing_tag = db.query(Tag).filter(Tag.name == tag.name, Tag.id != tag_id).first()
    if existing_tag:
        raise HTTPException(status_code=400, detail="Tag name already exists")
    
    for key, value in tag.model_dump().items():
        setattr(db_tag, key, value)
    
    db.commit()
    db.refresh(db_tag)
    return db_tag

# DELETE A TAG
@router.delete("/{tag_id}", response_model=dict)
def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    db_tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if db_tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    db.delete(db_tag)
    db.commit()
    return {"message": f"Tag with id {tag_id} deleted successfully"}