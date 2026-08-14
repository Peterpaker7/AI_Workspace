class sf:
    @staticmethod
    def conversion(y_train,stk_data):
        import pandas as pd
        Actual_y_train=pd.DataFrame(index=range(len(y_train)),columns=stk_data.columns)
        for i in range(len(y_train)):
            Actual_y_train.iloc[i]=y_train[i]
        return Actual_y_train

    @staticmethod
    def rmsemape(y_test,predicted_stock_price_test_ori):
        from sklearn.metrics import mean_squared_error
        print("RMSE-Testset : ",mean_squared_error(y_test,predicted_stock_price_test_ori,squared=False))
        from sklearn.metrics import mean_absolute_percentage_error
        print('maPe-testset : ',mean_absolute_percentage_error(y_test,predicted_stock_price_test_ori))

    @staticmethod
    def conversionSingle(y_train,stk_data):
        import pandas as pd
        Actual_y_train=pd.DataFrame(index=range(len(y_train)),columns=stk_data)
        for i in range(len(y_train)):
            Actual_y_train.iloc[i]=y_train[i]
        return Actual_y_train

    @staticmethod
    def graph(Actual_predicted,Actlabel,predlabel,title,Xlabel,ylabel):
        from matplotlib import pyplot as plt
        plt.figure(figsize=(10,5))
        plt.plot(Actual,color='blue',label=Actlabel)
        plt.plot(predicted,color='green',label=predlabel)
        plt.title(title)
        plt.xlabel(Xlabel)
        plt.ylabel(ylabel)
        plt.legend()
        plt.show()
        