"""
Data module - temporary forwarding to root modules during migration
This allows both old and new import paths to work
"""

import sys
import os

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import from root modules and re-export
try:
    # Import from database.py
    import importlib.util
    
    # Import database module
    spec = importlib.util.spec_from_file_location("database_root", os.path.join(parent_dir, "database.py"))
    database_root = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(database_root)
    
    # Import data_tracking module
    spec2 = importlib.util.spec_from_file_location("data_tracking_root", os.path.join(parent_dir, "data_tracking.py"))
    data_tracking_root = importlib.util.module_from_spec(spec2)
    spec2.loader.exec_module(data_tracking_root)
    
    # Re-export from database.py
    Base = database_root.Base
    User = database_root.User
    Simulation = database_root.Simulation
    UsageStats = database_root.UsageStats
    SessionLocal = database_root.SessionLocal
    init_db = database_root.init_db
    
    # Re-export from data_tracking.py
    save_simulation = data_tracking_root.save_simulation
    save_full_simulation = data_tracking_root.save_full_simulation
    load_simulation = data_tracking_root.load_simulation
    get_user_simulations = data_tracking_root.get_user_simulations
    delete_simulation = data_tracking_root.delete_simulation
    update_simulation_name = data_tracking_root.update_simulation_name
    
except Exception as e:
    print(f"Warning: Could not import from root data modules: {e}")
    raise
