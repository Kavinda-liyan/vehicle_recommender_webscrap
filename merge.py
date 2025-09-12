import pandas as pd

petrol_df=pd.read_csv("./datasets/petrol_vehicles_c.csv")
diesel_df=pd.read_csv("./datasets/diesel_vehicles_c.csv")
hybrid_df=pd.read_csv("./datasets/hybrid_vehicles_c.csv")
ev_df=pd.read_csv("./datasets/electric_vehicles_c.csv")

all_vehicles=pd.concat([petrol_df,diesel_df,hybrid_df,ev_df],ignore_index=True)
all_vehicles=all_vehicles.sort_values(by=["Manufacturer", "Year", "Model"], ascending=[True, False, True])
all_vehicles.to_csv("./datasets/all_vehicles.csv",index=False)
print(f"Cleaned and saved to all_vehicles.csv with {len(all_vehicles)} vehicles")