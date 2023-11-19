import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
import matplotlib.pyplot as plt
import numpy as np


class Knngroping:
    def __init__(self, df:pd.DataFrame):
        self.df = df # rvisualizer.df.copy() #전처리 한 후 사용
        self._set_data()


    def _set_data(self):
        self.df = self.df.pivot_table(index=['maker', 'product'], columns=['header', 'label'],
                                        values=['score', 'result_value'],
                                        aggfunc={'score': 'first', 'result_value': 'first'}).reset_index()

    #
    #
    def plot_dt(self):


        numeric_columns = ddf_pivot.select_dtypes(include=['int64', 'float64']).columns
        X_numeric = ddf_pivot[numeric_columns]

        # 범주형 변수 추출 및 더미 변수 생성
        categorical_columns = ddf_pivot.select_dtypes(include=['object']).columns
        X_categorical = pd.get_dummies(ddf_pivot[categorical_columns], drop_first=True)

        scaler = StandardScaler()
        X_numeric_scaled = scaler.fit_transform(X_numeric)

        # 수치형 변수와 더미 변수 결합
        X_combined = pd.concat([pd.DataFrame(X_numeric_scaled, columns=numeric_columns), X_categorical], axis=1)

        # PCA를 사용하여 2차원으로 차원 축소
        pca = PCA(n_components=2)
        X_pca = pca.fit_transform(X_combined)



        # 시각화
        plt.figure(figsize=(12, 8))

        # 데이터 포인트를 산점도로 표시
        plt.scatter(X_pca[:, 0], X_pca[:, 1], c=cluster_assignments, cmap='viridis', edgecolors='k', s=50)

        # KNN 모델의 결정 경계 표시
    #     h = .02
    #     x_min, x_max = X_pca[:, 0].min() - 1, X_pca[:, 0].max() + 1
    #     y_min, y_max = X_pca[:, 1].min() - 1, X_pca[:, 1].max() + 1
    #
    #     xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))
    #     Z = knn_model.predict(np.c_[xx.ravel(), yy.ravel()])
    #     Z = Z.reshape(xx.shape)
    #
    #     plt.contourf(xx, yy, Z, alpha=0.3, cmap='viridis')
    #
    #     plt.title('KNN Clustering with 2D Visualization')
    #     plt.xlabel('Principal Component 1')
    #     plt.ylabel('Principal Component 2')
    #     plt.show()
