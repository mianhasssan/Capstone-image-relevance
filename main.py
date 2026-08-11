import os
from fastapi import FastAPI, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session
from database import engine, Base, get_db
import models
import schemas
from vision_service import process_image_with_ai
from embedding_service import get_text_embedding
from matching_service import cosine_similarity, run_mismatch_guard
import glob

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Image Understanding Engine")

def process_images_batch(db: Session):
    """Background task to scan the images directory and process them via AI"""
    image_files = glob.glob("images/*.jpg")
    
    for filepath in image_files:
        filename = os.path.basename(filepath)
        
        # Check if already processed
        existing = db.query(models.Image).filter(models.Image.filename == filename).first()
        if existing:
            continue
            
        print(f"Processing new image: {filename}")
        try:
            result = process_image_with_ai(filepath)
            tags = result["tags"]
            cost = result["cost"]
            
            # Generate embedding from tags
            embedding_text = f"Subject: {tags['subject']}. Category: {tags['category']}. Caption: {tags['caption']}. Attributes: {', '.join(tags['attributes'])}"
            embedding_vector = get_text_embedding(embedding_text)
            
            # Save to DB
            new_image = models.Image(filename=filename, filepath=filepath)
            db.add(new_image)
            db.commit()
            db.refresh(new_image)
            
            metadata = models.ImageMetadata(
                image_id=new_image.id,
                subject=tags["subject"],
                category=tags["category"],
                attributes=tags["attributes"],
                caption=tags["caption"],
                confidence=tags["confidence"],
                embedding=embedding_vector,
                api_cost=cost
            )
            db.add(metadata)
            db.commit()
            print(f"Successfully tagged & embedded {filename} (Cost: ${cost})")
        except Exception as e:
            print(f"Failed to process {filename}: {str(e)}")
            db.rollback()

@app.post("/images/process-batch")
def start_batch_processing(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Triggers the background job to process images"""
    background_tasks.add_task(process_images_batch, db)
    return {"message": "Batch processing started in the background"}

@app.get("/images")
def get_images(db: Session = Depends(get_db)):
    """View processed images and metadata"""
    images = db.query(models.Image).all()
    return [{
        "filename": img.filename,
        "metadata": img.metadata_info.subject if img.metadata_info else None
    } for img in images]

@app.post("/posts", response_model=schemas.PostResponse)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db)):
    """Create a new blog post and generate its embedding"""
    embedding_vector = get_text_embedding(post.content)
    new_post = models.Post(
        content=post.content,
        expected_category=post.expected_category,
        embedding=embedding_vector
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@app.get("/posts/{post_id}/images", response_model=schemas.MatchResult)
def rank_images_for_post(post_id: str, db: Session = Depends(get_db)):
    """Finds the best image for a post and runs the mismatch guard"""
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
        
    images = db.query(models.Image).all()
    if not images:
        return schemas.MatchResult(status="REJECTED", reason="No images in library")
        
    # Rank all images by cosine similarity
    ranked = []
    for img in images:
        if img.metadata_info and img.metadata_info.embedding:
            sim = cosine_similarity(post.embedding, img.metadata_info.embedding)
            ranked.append((sim, img))
            
    if not ranked:
        return schemas.MatchResult(status="REJECTED", reason="No embedded images found in library")

    # Sort descending
    ranked.sort(key=lambda x: x[0], reverse=True)
    
    # Get the best candidate
    best_sim, best_img = ranked[0]
    
    # Run the guard
    result = run_mismatch_guard(post, best_img, best_sim)
    
    if result.status == "APPROVED":
        # Save a pending suggestion to the DB for human review
        suggestion = models.Suggestion(
            post_id=post.id,
            image_id=best_img.id,
            similarity_score=best_sim,
            status="pending"
        )
        db.add(suggestion)
        db.commit()
        db.refresh(suggestion)
        result.suggestion_id = suggestion.id
        
    return result

@app.post("/suggestions/{suggestion_id}/approve", response_model=schemas.SuggestionResponse)
def approve_suggestion(suggestion_id: str, db: Session = Depends(get_db)):
    """Human-in-the-loop: Approve an image suggestion"""
    suggestion = db.query(models.Suggestion).filter(models.Suggestion.id == suggestion_id).first()
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")
        
    suggestion.status = "approved"
    db.commit()
    db.refresh(suggestion)
    return suggestion

@app.post("/suggestions/{suggestion_id}/reject", response_model=schemas.SuggestionResponse)
def reject_suggestion(suggestion_id: str, db: Session = Depends(get_db)):
    """Human-in-the-loop: Reject an image suggestion"""
    suggestion = db.query(models.Suggestion).filter(models.Suggestion.id == suggestion_id).first()
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")
        
    suggestion.status = "rejected"
    db.commit()
    db.refresh(suggestion)
    return suggestion
