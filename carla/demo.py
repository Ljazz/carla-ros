import cv2
import sys
import time

dt = "2019-01-23 15:29:00"
# 转换成时间数组
timeArray = time.strptime(dt, "%Y-%m-%d %H:%M:%S")
# 转换成时间戳
timestamp = time.mktime(timeArray)
print(timeArray)
print(timestamp)


cap_1 = cv2.VideoCapture(1)
cap_1.set(3, 1920)
cap_1.set(4, 1080)
# cap_2 = cv2.VideoCapture(2)
# cap_3 = cv2.VideoCapture(3)
# cap_4 = cv2.VideoCapture(4)

write_ok = False

sz = (int(cap_1.get(cv2.CAP_PROP_FRAME_WIDTH)),
      int(cap_1.get(cv2.CAP_PROP_FRAME_HEIGHT)))
fps = 30
fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
# fourcc = cv2.VideoWriter_fourcc(*'mpeg')


vout_1 = cv2.VideoWriter()
vout_1.open('./1/output.mp4', fourcc, fps, sz, True)
# vout_2 = cv2.VideoWriter()
# vout_2.open('./2/output.mp4',fourcc,fps,sz,True)
# vout_3 = cv2.VideoWriter()
# vout_3.open('./3/output.mp4',fourcc,fps,sz,True)


cnt = 0
while(True):
    if(write_ok):
        # print("video")
        # 获取当前时间
        time_now = int(time.time())
        # 转换成localtime
        # time_local = time.localtime(time_now)
        print(time_now)
        if time_now >= timestamp:
            while(cnt < 900):
                cnt += 1
                print(cnt)

                ret_1, frame_1 = cap_1.read()
                vout_1.write(frame_1)

                # ret_2, frame_2 = cap_2.read()
                # vout_2.write(frame_2)

                # ret_3, frame_3 = cap_3.read()
                # vout_3.write(frame_3)

            vout_1.release()
            # vout_2.release()
            # vout_3.release()
            sys.exit()
    else:
        print("stop")
        ret_1, frame_1 = cap_1.read()
        cv2.imshow("cam_1", frame_1)
        # ret_2, frame_2 = cap_2.read()
        # cv2.imshow("cam_2", frame_2)
        # ret_3, frame_3 = cap_3.read()
        # cv2.imshow("cam_3", frame_3)

    if cv2.waitKey(1) & 0xFF == ord("w"):
        write_ok = write_ok is not True
