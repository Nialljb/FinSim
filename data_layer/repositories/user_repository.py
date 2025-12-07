"""
User repository for data access
Implements repository pattern for User model
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from data_layer.database import User


class UserRepository:
    """Repository for User model operations"""
    
    def __init__(self, db: Session):
        """
        Initialize repository with database session
        
        Args:
            db: SQLAlchemy session
        """
        self.db = db
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.db.query(User).filter(User.username == username).first()
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_by_username_or_email(self, identifier: str) -> Optional[User]:
        """Get user by username or email"""
        return self.db.query(User).filter(
            (User.username == identifier) | (User.email == identifier)
        ).first()
    
    def create(
        self,
        username: str,
        email: str,
        hashed_password: str,
        current_age: int,
        target_retirement_age: int,
        country: Optional[str] = None,
        data_sharing_consent: bool = False
    ) -> User:
        """
        Create new user
        
        Args:
            username: Unique username
            email: User email
            hashed_password: Hashed password (not plain text!)
            current_age: User's current age
            target_retirement_age: Target retirement age
            country: Optional country
            data_sharing_consent: Data sharing consent
        
        Returns:
            Created User object
        """
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            current_age=current_age,
            target_retirement_age=target_retirement_age,
            country=country,
            data_sharing_consent=data_sharing_consent,
            email_verified=False  # Requires verification
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def update(self, user: User) -> User:
        """
        Update existing user
        
        Args:
            user: User object with updated fields
        
        Returns:
            Updated User object
        """
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def delete(self, user: User) -> None:
        """
        Delete user
        
        Args:
            user: User object to delete
        """
        self.db.delete(user)
        self.db.commit()
    
    def list_all(self, limit: Optional[int] = None) -> List[User]:
        """
        List all users
        
        Args:
            limit: Optional limit on number of results
        
        Returns:
            List of User objects
        """
        query = self.db.query(User)
        if limit:
            query = query.limit(limit)
        return query.all()
    
    def list_unverified(self) -> List[User]:
        """Get all users who haven't verified their email"""
        return self.db.query(User).filter(User.email_verified == False).all()
    
    def verify_email(self, user: User) -> User:
        """Mark user's email as verified"""
        user.email_verified = True
        return self.update(user)
    
    def increment_simulation_count(self, user: User) -> User:
        """Increment user's simulation count"""
        user.simulation_count = (user.simulation_count or 0) + 1
        return self.update(user)
    
    def increment_export_count(self, user: User) -> User:
        """Increment user's export count"""
        user.export_count = (user.export_count or 0) + 1
        return self.update(user)
    
    def reset_simulation_count(self, user: User) -> User:
        """Reset user's simulation count to 0"""
        user.simulation_count = 0
        return self.update(user)
    
    def exists(self, username: Optional[str] = None, email: Optional[str] = None) -> bool:
        """
        Check if user exists with given username or email
        
        Args:
            username: Username to check
            email: Email to check
        
        Returns:
            True if user exists, False otherwise
        """
        query = self.db.query(User)
        
        if username and email:
            query = query.filter((User.username == username) | (User.email == email))
        elif username:
            query = query.filter(User.username == username)
        elif email:
            query = query.filter(User.email == email)
        else:
            return False
        
        return query.first() is not None
