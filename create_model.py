from numpy import load;
from sklearn.svm import SVC;
from sklearn.metrics import mean_squared_error, accuracy_score;
from matplotlib import pyplot as plt;
from sklearn.preprocessing import LabelEncoder;
import pickle;

data=load("data/data.npz",allow_pickle=True);
trainX, trainy, testX, testy = data['arr_0'],data['arr_1'],data['arr_2'],data['arr_3'];
trainX=trainX.reshape(trainX.shape[0],trainX.shape[1]);
testX=testX.reshape(testX.shape[0],testX.shape[1]);
print('Dataset: trainX=%s, testX=%s' % (trainX.shape, testX.shape));
print('Dataset: trainy=%s, testy=%s' % (trainy.shape, testy.shape));

out_encoder=LabelEncoder();
out_encoder.fit(trainy);
trainy=out_encoder.transform(trainy);
testy=out_encoder.transform(testy);

model=SVC(kernel='linear',probability=True);
model.fit(trainX,trainy);
pickle.dump(model,open("data/atm_model.sav","wb"))

output_train=model.predict(trainX);
output_test=model.predict(testX);

score_train=accuracy_score(trainy,output_train);
score_test=accuracy_score(testy,output_test);
print('Accuracy: train=%.3f, test=%.3f' % (score_train*100, score_test*100));
print("MSE:%.4f"%mean_squared_error(testy,output_test));

x_ax = range(len(output_test))
plt.scatter(x_ax, testy, s=5, color="blue", label="Original")
plt.plot(x_ax, output_test, lw=0.8, color="red", label="Predicted")
plt.legend()
plt.show()
