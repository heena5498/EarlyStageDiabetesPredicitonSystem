import pytest
import pandas as pd
from src.adapters.pima import PimaAdapter

def test_pima_adapter_structure():
    """
    Verify that PimaAdapter initializes correctly and follows the BaseAdapter contract.
    """
    adapter = PimaAdapter(
        path="tests/dummy_pima.csv", 
        country="USA", 
        year=2024, 
        source_id="test_pima"
    )
    
    assert adapter.country == "USA"
    assert adapter.source_id == "test_pima"
    
    assert hasattr(adapter, "load_raw")
    assert hasattr(adapter, "to_silver")