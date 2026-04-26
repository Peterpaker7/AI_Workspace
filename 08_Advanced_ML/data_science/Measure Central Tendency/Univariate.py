class SplitOF():
    @staticmethod
    def QuanQual(dataset):
        Quan=[]
        Qual=[]
        for columnName in dataset.columns:
            if dataset[columnName].dtype=='O':
                Qual.append(columnName)
            else:
                Quan.append(columnName)
        return Quan,Qual
    
    def frequTable(columnName,dataset):
        freqTable=pd.DataFrame(columns=["Unique_Values",'Frequence','Relative_Frequence','Cumulative_Frequence'])
        freqTable["Unique_Values"]=dataset[columnName].value_counts().index
        freqTable['Frequence']=dataset[columnName].value_counts().values
        freqTable['Relative_Frequence']=freqTable['Frequence']/103
        freqTable['Cumulative_Frequence']=freqTable['Relative_Frequence'].cumsum()

        return freqTable

    def Univariate(dataset,quan):
        descrptive=pd.DataFrame(index=["Mean",'Medain','Mode',"Q1:25%","Q2:50%","Q3:75%","Q4:100%","Min","Max","IQR",'1.5rule',"Lesser",'greater'],columns=quan)
        for columnName in quan:
            descrptive[columnName]['Mean']=dataset[columnName].mean()
            descrptive[columnName]["Medain"]=dataset[columnName].median()
            descrptive[columnName]["Mode"]=dataset[columnName].mode()[0]
            descrptive[columnName]["Q1:25%"]=dataset.describe()[columnName]["25%"]
            descrptive[columnName]["Q2:50%"]=dataset.describe()[columnName]["50%"]
            descrptive[columnName]["Q3:75%"]=dataset.describe()[columnName]["75%"]
            descrptive[columnName]["Q4:100%"]=dataset.describe()[columnName]["max"]
            descrptive[columnName]["Min"]=dataset.describe()[columnName]['min']
            descrptive[columnName]["Max"]=dataset.describe()[columnName]["max"]
            descrptive[columnName]["IQR"]=descrptive[columnName]["Q3:75%"]-descrptive[columnName]["Q1:25%"]
            descrptive[columnName]["1.5rule"]=1.5*descrptive[columnName]["IQR"]
            descrptive[columnName]["Lesser"]=descrptive[columnName]["Q1:25%"]-descrptive[columnName]['1.5rule']
            descrptive[columnName]['greater']=descrptive[columnName]["Q3:75%"]-descrptive[columnName]['1.5rule']

        return descrptive
    

