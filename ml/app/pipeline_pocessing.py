import numpy as np
import cv2

def yolo_procces(request_id):
    cap = cv2.VideoCapture(f'./media/{request_id}-rgb.mp4')

    classesFile = 'coco.names'
    classesNames = []
    foodClassesFile = 'food.names'
    foodClassesNames = []
    confsTresHold = 0.5
    nmsTresHold = 0.3
    with open(classesFile, 'rt') as f:
        classesNames = f.read().rstrip('\n').split('\n')
    
    with open(foodClassesFile, 'rt') as f:
        foodClassesNames = f.read().rstrip('\n').split('\n')
        
    # modelConfiguration = 'yolov2-food100.cfg'
    # modelWeights = 'yolov2-food100_10000.weights'
    modelConfiguration = 'yolov3-320.cfg'
    modelWeights = 'yolov3-320.weights'

    net = cv2.dnn.readNetFromDarknet(modelConfiguration, modelWeights)
    net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
    net.setPreferableTarget(cv2.dnn.DNN_TARGET_OPENCL)

    def findObjects(outputs, img):
        hT, wT, cT = img.shape
        bbox = []
        classIds = []
        confs = []

        for output in outputs:
            for det in output:
                scores = det[5:]
                classId = np.argmax(scores)
                confidence = scores[classId]
                if confidence > confsTresHold:
                    w, h = int(det[2] * wT), int(det[3] * hT)
                    x, y = int((det[0] * wT) - w/2), int((det[1] * hT) - h/2)
                    bbox.append([x, y, w, h])
                    classIds.append(classId)
                    confs.append(float(confidence))

        indices = cv2.dnn.NMSBoxes(bbox, confs, confsTresHold, nmsTresHold)

        for i in indices:
            if not(classesNames[classIds[i]] in foodClassesNames):
                continue
            box = bbox[i]
            x, y, w, h = int(box[0]), int(box[1]), int(box[2]), int(box[3])
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
            cv2.putText(img, f'{classesNames[classIds[i]]}: {confs[i] * 100}%', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)

    format_video_pipeline = cv2.VideoWriter_fourcc(*'H264') # формат видео
    video_from_pipeline = cv2.VideoWriter(f'./media/{request_id}-pipline.mp4', format_video_pipeline, 15.0, (640, 480))

    length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(length)
    for i in range(length):
        print(i)
        success, img = cap.read()

        blob = cv2.dnn.blobFromImage(img, 1/255, (480, 640),[0,0,0], 1, crop=False)
        net.setInput(blob)

        layerNames = net.getLayerNames()

        outputNames = [layerNames[i - 1] for i in net.getUnconnectedOutLayers()]

        outputs = net.forward(outputNames)

        findObjects(outputs, img)
        video_from_pipeline.write(img)

    video_from_pipeline.release()