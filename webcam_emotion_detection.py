# load saved model
from tensorflow.keras.models import model_from_json
model = model_from_json(open("model.json", "r").read())
model.load_weights('model.h5')

# load Haar-cascade used to detect position of face
import cv2
face_haar_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# capture webcam feed and detect emotion
cap = cv2.VideoCapture(0) # open default camera
while cap.isOpened():
    # capture frame by frame
    res, frame = cap.read()
    height, width, channel = frame.shape

    # create overlay to display prediction and degree of confidence
    # TODO: customize
    sub_img = frame[0:int(height/6), 0:int(width)]
    black_rect = np.ones(sub_img.shape, dtype=np.uint8) * 0
    res = cv2.addWeighted(sub_img, 0.77, black_rect, 0.23, 0)
    FONT = cv2.FONT_HERSHEY_SIMPLEX
    FONT_SCALE = 0.8
    FONT_THICKNESS = 2
    lable_color = (10, 10, 255)
    lable = "How Are You Really?"
    lable_dimension = cv2.getTextSize(lable, FONT, FONT_SCALE, FONT_THICKNESS)[0]
    textX = int((res.shape[1] - lable_dimension[0]) / 2)
    textY = int((res.shape[0] + lable_dimension[1]) / 2)

    # make prediction
    # haar_cascade only takes grayscale images; convert into grayscale
    gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # detect position of face
    faces = face_haar_cascade.detectMultiScale(gray_image)  
    try:
        for (x, y, w, h) in faces:
            # draw rectangle around detected face
            cv2.rectangle(frame, pt1=(x, y), pt2=(x+w, y+h), color=(255, 0, 0), thickness=2)
            # tailor image to feed model
            roi_gray = gray_image[y-5:y+h+5, x-5:x+w+5]
            roi_gray = cv2.resize(roi_gray, (48, 48))
            image_pixels = img_to_array(roi_gray)
            image_pixels = np.expand_dims(image_pixels, axis = 0) # convert 3d matrix into 4d tensor
            image_pixels /= 255 # normalize
            # use model to predict emotion
            predictions = model.predict(image_pixels)
            max_index = np.argmax(predictions[0])
            emotion_detection = ('angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral')
            emotion_prediction = emotion_detection[max_index]
            # set overlay
            # TODO: customize
            cv2.putText(res, 'Emotion: {}'.format(emotion_prediction), (0, textY+22+5), FONT, 0.7, lable_color, 2)
            lable_violation = 'Confidence: {}'.format(str(np.round(np.max(predictions[0]) * 100, 1)) + "%")
            violation_text_dimension = cv2.getTextSize(lable_violation, FONT, FONT_SCALE, FONT_THICKNESS)[0]
            violation_x_axis = int(res.shape[1] - violation_text_dimension[0])
            cv2.putText(res, lable_violation, (violation_x_axis, textY+22+5), FONT, 0.7, lable_color, 2)
    except:
        pass
    
    # add overlay
    frame[0:int(height/6), 0:int(width)] = res
    # display modified frame
    cv2.imshow('frame', frame)
    # type q to exit webcam
    if cv2.waitKey(1) == ord('q'):
        break

# when everything done, release the capture
cap.release()
cv2.destroyAllWindows