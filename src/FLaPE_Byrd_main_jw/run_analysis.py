import pandas as pd
import numpy as np

# 1. Import the class
from ReachObservations_jw import ReachObservations

# 2. Load the REAL data
print("Loading real SWOT data...")
df = pd.read_csv('src/FLaPE_Byrd_main_jw/godavari_swot_cleaned.csv')
df['time'] = pd.to_datetime(df['time'])

# 3. Select a single reach to act as nR=1
# We will automatically find the reach with the most observations
target_reach = df['reach_id'].value_counts().idxmax()
reach_df = df[df['reach_id'] == target_reach].sort_values('time')

nt_real = len(reach_df)
print(f"Selected Reach ID: {target_reach} with {nt_real} time steps.")

# 4. Create the Domain Object tailored to the real data dimensions
class DomainObject:
    def __init__(self, nR, nt):
        self.nR = nR
        self.nt = nt
        # Create a time array (0 to nt) for plotting purposes
        self.t = np.arange(self.nt).reshape(1, self.nt)
        
    def CalcU(self):
        # A dummy matrix function required by the area calculations
        return np.eye(self.nR * (self.nt - 1))

# Initialize Domain with 1 Reach and our actual number of time steps
D_obj = DomainObject(nR=1, nt=nt_real)

# 5. Extract the columns and format them into (nR, nt) arrays
# wse -> height (h), width -> width (w)
h_array = reach_df['wse'].values.reshape(1, nt_real)
w_array = reach_df['width'].values.reshape(1, nt_real)

# The class expects single values for uncertainty, so we take the mean 
# of the actual SWOT uncertainties for this specific reach
wse_u_mean = reach_df['wse_u'].mean()
width_u_mean = reach_df['width_u'].mean()

RiverData = {
    "h": h_array,
    "w": w_array,
    # The cleaned dataset does not have a slope column, so we provide dummy zeros
    # as the class only strictly needs 'h' and 'w' for the Area constraint math
    "S": np.zeros((1, nt_real)),            
    "h0": np.nanmedian(h_array),            # Baseline height (median of observations)
    "sigh": wse_u_mean,                     # Average WSE uncertainty from SWOT
    "sigw": width_u_mean,                   # Average Width uncertainty from SWOT
    "sigS": 0.0001                          # Dummy Slope uncertainty
}

# 6. RUN THE CODE
print("Initializing ReachObservations and calculating fits for Godavari data...")

# By setting Verbose=True, the script will generate plots mapping the SWOT 
# observations onto the piecewise hypsometric curve!
ro = ReachObservations(
    D=D_obj,
    RiverData=RiverData,
    CalcAreaFitOpt=3,       
    ConstrainHWSwitch=True, 
    Verbose=True            
)

print("Analysis complete!")