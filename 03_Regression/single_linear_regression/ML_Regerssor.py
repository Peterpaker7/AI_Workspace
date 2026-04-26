import pandas as pd
import pickle as p
from sklearn.model_selection import train_test_split as tts
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

dataset=pd.read_csv("C:\\Users\\USER\\Desktop\\ML-Regression\\Salary_Data.csv")
independant=dataset[["YearsExperience"]]
dependent=dataset["Salary"]
x_train,x_test,y_train,y_test=tts(independant,dependent,test_size=0.30,random_state=0)

regressor=LinearRegression()
regressor.fit(x_train,y_train)

weight=regressor.coef_
bais=regressor.intercept_

#print("Weight: ",weight)
#print("Bais: ",bais)

y_pred=regressor.predict(x_test)
r2_score(y_test,y_pred)
print("R2 Score: ",r2_score(y_test,y_pred))

#save the model
"""filename="finalized_model.sav"
p.dump(regressor,open(filename,'wb'))
#load the model
loaded_model=p.load(open(filename,'rb'))
result=loaded_model.predict([[5]])

print("Predicted Salary: ",result)"""



