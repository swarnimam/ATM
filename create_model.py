import os
from PIL import Image;
from mtcnn.mtcnn import MTCNN;
from keras_facenet import FaceNet;
from sklearn.preprocessing import Normalizer;
from numpy import asarray;
from keras.models import Sequential;
from keras.layers import Dense, Conv1D, Flatten;
from sklearn.metrics import mean_squared_error;
from matplotlib import pyplot as plt;

detector=MTCNN();
embedder=FaceNet();

def extract_face(filename,requiredsize=(160,160)):
    image=Image.open(filename);
    image=image.convert('RGB');
    pixels=asarray(image);
    results=detector.detect_faces(pixels);
    if len(results)==0:
        x1,y1,width,height=0,0,160,160;
    else:
        x1,y1,width,height=results[0]['box'];
    x1,y1=abs(x1),abs(y1);
    x2,y2=x1+width,y1+height;
    face=pixels[y1:y2,x1:x2];
    image=Image.fromarray(face);
    image=image.resize(requiredsize);
    face_array=asarray(image);
    return face_array;

def load_faces(folder):
    faces=list();
    for filename in os.listdir(folder):
        path=folder+filename;
        face=extract_face(path);
        faces.append(face);
    return faces;

def load_dataset(directory):
    X,y=list(),list();
    for subdir in os.listdir(directory):
        path=directory+subdir+"/";
        if not os.path.isdir(path):
            continue;
        faces=load_faces(path);
        labels=[int(subdir) for _ in range(len(faces))];
        print(">Loaded %d examples for : %s" % (len(faces),subdir));
        X.extend(faces);
        y.extend(labels);
    return asarray(X),asarray(y);

def create_embeddings(data):
    return embedder.embeddings(data);

train_X,train_y=load_dataset("data/train/");
test_X,test_y=load_dataset("data/test/");

trainX=create_embeddings(train_X);
trainy=train_y;
testX=create_embeddings(test_X);
testy=test_y;

in_encoder=Normalizer(norm='l2');
trainX=in_encoder.transform(trainX);
testX=in_encoder.transform(testX);

trainX=trainX.reshape(trainX.shape[0],trainX.shape[1],1);
testX=testX.reshape(testX.shape[0],testX.shape[1],1);

model=Sequential();
model.add(Conv1D(32,2,activation="relu",input_shape=(512,1)));
model.add(Flatten());
model.add(Dense(64,activation="relu"));
model.add(Dense(1));
model.compile(loss="mse",optimizer="adam");
model.summary();
model.fit(trainX,trainy,batch_size=2,epochs=300,verbose=0);
model.save('data/atm_model.h5');

predictedy=model.predict(testX);
print(model.evaluate(trainX,trainy));
print("MSE:%.4f"%mean_squared_error(testy,predictedy));

x_ax = range(len(predictedy))
plt.scatter(x_ax, testy, s=5, color="blue", label="Original")
plt.plot(x_ax, predictedy, lw=0.8, color="red", label="Predicted")
plt.legend()
plt.show()