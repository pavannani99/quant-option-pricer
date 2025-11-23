import sqlite3
import uuid
from datetime import datetime
from typing import List, Dict, Optional
import pandas as pd
from contextlib import contextmanager
import os


class DatabaseService:
    def __init__(self, db_type='sqlite', connection_string=None):
        """Initialize database service"""
        self.db_type = db_type
        
        if db_type == 'sqlite':
            if connection_string is None:
                db_dir = os.path.dirname(os.path.abspath(__file__))
                connection_string = os.path.join(db_dir, 'blackscholes.db')
            self.connection_string = connection_string
            self._initialize_sqlite()
        else:
            raise NotImplementedError("MySQL support not yet implemented")
    
    def _initialize_sqlite(self):
        """Initialize SQLite database with schema"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create inputs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS calculations (
                    calculation_id TEXT PRIMARY KEY,
                    spot_price REAL NOT NULL,
                    strike REAL NOT NULL,
                    volatility REAL NOT NULL,
                    time_to_expiry REAL NOT NULL,
                    interest_rate REAL NOT NULL,
                    call_purchase_price REAL DEFAULT 0.0,
                    put_purchase_price REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON calculations(created_at)")
            
            conn.commit()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        if self.db_type == 'sqlite':
            conn = sqlite3.connect(self.connection_string)
            conn.row_factory = sqlite3.Row
            try:
                yield conn
            finally:
                conn.close()
        else:
            raise NotImplementedError("MySQL support not yet implemented")
    
    def save_calculation(self, inputs: Dict) -> str:
        """
        Save a calculation to the database
        
        Args:
            inputs: Dictionary with calculation parameters
            
        Returns:
            calculation_id: UUID string
        """
        calculation_id = str(uuid.uuid4())
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO calculations (
                    calculation_id, spot_price, strike, volatility, 
                    time_to_expiry, interest_rate, call_purchase_price, put_purchase_price
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                calculation_id,
                inputs.get('spot_price'),
                inputs.get('strike'),
                inputs.get('volatility'),
                inputs.get('time_to_expiry'),
                inputs.get('interest_rate'),
                inputs.get('call_purchase_price', 0.0),
                inputs.get('put_purchase_price', 0.0)
            ))
            
            conn.commit()
        
        return calculation_id
    
    def get_calculation_history(self, limit: int = 100) -> pd.DataFrame:
        """
        Get calculation history
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            DataFrame with calculation history
        """
        with self.get_connection() as conn:
            query = """
                SELECT 
                    calculation_id,
                    spot_price,
                    strike,
                    volatility,
                    time_to_expiry,
                    interest_rate,
                    call_purchase_price,
                    put_purchase_price,
                    created_at
                FROM calculations
                ORDER BY created_at DESC
                LIMIT ?
            """
            df = pd.read_sql_query(query, conn, params=(limit,))
            return df
    
    def get_calculation_by_id(self, calculation_id: str) -> Dict:
        """
        Retrieve a specific calculation by ID
        
        Args:
            calculation_id: UUID string
            
        Returns:
            Dictionary with calculation data
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM calculations WHERE calculation_id = ?
            """, (calculation_id,))
            
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Calculation {calculation_id} not found")
            
            result = dict(row)
            return result
    
    def delete_calculation(self, calculation_id: str):
        """
        Delete a calculation
        
        Args:
            calculation_id: UUID string
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM calculations WHERE calculation_id = ?", (calculation_id,))
            conn.commit()
    
    def get_statistics(self) -> Dict:
        """
        Get database statistics
        
        Returns:
            Dictionary with statistics
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) as count FROM calculations")
            total_calculations = cursor.fetchone()[0]
            
            # Total outputs = total calculations * 2 (call + put for each calculation)
            total_outputs = total_calculations * 2
            
            cursor.execute("""
                SELECT MIN(created_at) as first, MAX(created_at) as last 
                FROM calculations
            """)
            row = cursor.fetchone()
            
            return {
                'total_calculations': total_calculations,
                'total_outputs': total_outputs,
                'first_calculation': row[0] if row[0] else None,
                'last_calculation': row[1] if row[1] else None
            }
