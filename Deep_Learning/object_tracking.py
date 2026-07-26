import cv2
from ultralytics import YOLO

#Load the YOLO model
model = YOLO("yolov8n.pt")

#Open Webcam
cap = cv2.VideoCapture(0)

#Horizontal Counting line
line_y=300

#store counted IDs
counted_ids = set()
person_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    #Track only persons (COCO Class 0)
    results = model.track(
        frame,
        persist=True,
        classes=[0], #Person only
        verbose=False
    )

    #Draw Counting line
    cv2.line(frame, (0, line_y), (frame.shape[1], line_y), (0, 0, 255), 2)

    if results[0].boxes.id is not None:
        boxes = results[0].boxes.xyxy.cpu().numpy().astype(int)
        ids = results[0].boxes.id.cpu().numpy().astype(int)

        for box,track_id in zip(boxes, ids):
            x1, y1, x2, y2 = map(int,box)
            #Centre of bounding box
            cx = int((x1 + x2) // 2)
            cy = int((y1 + y2) //2)

            #Draw bounding box and ID
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.circle(frame,((x,cy),4,(255,0,0),-1))
            cv2.putText(frame, f'ID: {track_id}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            #Count When Crossing the Line
            if cy < line_y and track_id not in counted_ids:
                counted_ids.add(track_id)
                person_count += 1

            #Display Count
            cv2.putText(frame,f"Persons Counted :{person_count}",(20,40),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)
            cv2.imshow('Person Counter',frame)

            if cv2.waitKey(1)&0xFF==ord('q'):
                break
cap.release()
cv2.destroyAllWindows()