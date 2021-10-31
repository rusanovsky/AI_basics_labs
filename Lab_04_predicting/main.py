import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

df = pd.read_csv("data.csv", delimiter=",")

df['result'].replace(['win', 'lose'], [1, 0], inplace=True)

results_with_minmax = df[df["algo"] == 1]["result"].to_numpy()
results_with_expect = df[df["algo"] == 2]["result"].to_numpy()

values_for_minimax = [len(np.where(results_with_minmax == 0)[0]), len(np.where(results_with_minmax == 1)[0])]
values_for_expect = [len(np.where(results_with_expect == 0)[0]), len(np.where(results_with_expect == 1)[0])]
_, axes = plt.subplots(ncols=2, nrows=1, figsize=(10, 5))
axes[0].pie(values_for_minimax, labels=["Поразка", "Перемога"], autopct="%1.1f%%", shadow=True)
axes[0].set_title("Результати перемоги Пакмана \n для алгоритму Мінімакс")
axes[1].pie(values_for_expect, labels=["Поразка", "Перемога"], autopct="%1.1f%%", shadow=True)
axes[1].set_title("Результати перемоги Пакмана \n для алгоритму Експектімакс")
plt.show()

x = df[["algo"]].to_numpy()
y = df["result"].to_numpy()
train_x, test_x, train_y, test_y = train_test_split(x, y, test_size=0.1)
model = LogisticRegression()
model.fit(train_x, train_y)

predict = model.predict(test_x)

print("Точність моделі: ", accuracy_score(test_y, predict))

next_5_games_algo = np.array([1, 1, 1, 2, 2]).reshape(-1, 1)

predict_for_next_games = model.predict(next_5_games_algo)
predict_for_next_games_prob = model.predict_proba(next_5_games_algo)
for i in range(len(predict_for_next_games)):
    result = "Поразка" if predict_for_next_games[i] == 0 else ""
    print(f"Очікувані результати гри №{i}: {result},\n \t ймовірність виграти = {predict_for_next_games_prob[i][1]}\n"
          f" \t ймовірність програти = {predict_for_next_games_prob[i][0]}")