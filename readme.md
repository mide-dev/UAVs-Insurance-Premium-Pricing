# This repo computes Insurance premiums for UAVs (Drones) based on weight, price and other factors.

## Project Structure

- `model_operations.py`: Contains classes and methods for premium calculations.
  - `BaseModelOperations`: Base class with common operations for premium calculations.
  - `DroneOperations`: Inherits from `BaseModelOperations` and provides drone-specific calculations.
  - `CameraOperations`: Inherits from `BaseModelOperations` and provides camera-specific calculations.
  - `PremiumAdjustments`: Provides methods for adjusting premiums based on constraints.
- `main.py`: The main script that executes the model computations and outputs the results.
- `config.json`: Contains parameters and rates used in the calculations.
- `data_loader.py`: Contains the provided example data.
- `test_operations.py`: Contains unit tests for the core classes and their functionalities.

## Dependencies

- Python 3.x
- Standard Python libraries: `math`, `json`, `typing`

## Usage

1. **Run the Model:**
   Execute the main script to perform the calculations: **`python main.py`**

2. **View the Results:**
   The script will output a JSON-formatted string containing the computed premiums and any adjustments applied.

## Testing

Run unit tests to verify the functionality of the core classes: **`python test_operations.py`**
