import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("postgresql://vmmfszxyquhraz:dde9deee8b575db7a8f4214d70e99429a5bb1a73d018ce8665642754005ed4ed@ec2-52-86-73-86.compute-1.amazonaws.com:5432/d1l9tnctjr6utu")

df = pd.read_sql(sql="SELECT * FROM user;", con=engine)
print(df)