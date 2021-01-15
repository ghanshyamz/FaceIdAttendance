import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime,date
import DatabaseHelper as dh

useDATABASE = 1    #if '1' entry will be recorded in database, if '0' then in a CSV file
path = 'AttendanceImages'
images = []
classNames = []
myList = os.listdir(path)
print(myList)

for cls in myList :
    curImg = cv2.imread(f'{path}/{cls}')
    images.append(curImg)
    classNames.append(os.path.splitext(cls)[0])
print(classNames)

def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList


def markAttendanceCSV(name):
    with open("Attendance.csv","r+") as f:
        myDataList = f.readlines()
        nameList = []
        for line in myDataList:
            entry = line.split(",")
            nameList.append(entry[0])
        if name not in nameList:
            now = datetime.now()
            dtString = now.strftime("%H:%M:%S")
            f.writelines(f"\n{name},{dtString}")

def markAttendanceDATABASE(name):
    conn,cur = dh.connectToDatabase()
    if dh.checkInDatabase(cur,name):
        return
    else:
        now = datetime.now()
        today = date.today()
        timeString = now.strftime("%H:%M:%S")
        dateString = today.strftime("%Y-%m-%d")
        print(timeString,dateString)
        dh.insertToDatabase(cur,name,timeString,dateString)
    
    conn.commit()
    cur.close()
    conn.close()


    

encodeListKnown = findEncodings(images)
print("Encoding Complete")

cap = cv2.VideoCapture(0)

while True:
    success, img = cap.read()
    imgS = cv2.resize(img,(0,0),None,0.50,0.50) #to perform operations faster img size is reduced 0.25
    imgS = cv2.cvtColor(imgS,cv2.COLOR_BGR2RGB)

    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS,facesCurFrame)

    for encodeFace,faceLoc in zip(encodesCurFrame,facesCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown,encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown,encodeFace)
        #print(faceDis)
        matchIndex = np.argmin(faceDis)

        if matches[matchIndex]:
            name = classNames[matchIndex].upper()
            print(name)
            y1, x2, y2, x1 = faceLoc
            print(x1,y1,x2,y2)
            #to resize the rectangle to original size   
            y1, x2, y2, x1 = y1*2, x2*2, (y2*2)+40 , x1*2  
            print(x1,y1,x2,y2)
            cv2.rectangle(img,(x1,y1-40),(x2,y2),(0,255,0),2)
            cv2.rectangle(img,(x1,y2-35),(x2,y2),(0,255,0),cv2.FILLED)
            cv2.putText(img,name,(x1+6,y2-6),cv2.FONT_HERSHEY_COMPLEX,0.5,(255,255,255),1)
            if useDATABASE:
                markAttendanceDATABASE(name)
            else:
                markAttendanceCSV(name)

    cv2.imshow("Webcam",img)
    cv2.waitKey(1)