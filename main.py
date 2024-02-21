if __name__ == "__main__":
    '''
    
    Rules:
        No usage of threading (if not made sure they will die at end of the 10 minute, only using threading library)
        Well documented
        No errors
        does not start system processes.
        No networking
        max runtime is 10min (we have to create a timer to kill itself)
        have to use atleast one Sense HAT sensor.
        No fucking or swearing
    
    python 3.9.2
    
    install libraires:
    - skyfield
    - picamera
    - gpiozero
    - nympy
    - logzero
    - opencv-python
    - sense_hat
        https://sense-hat.readthedocs.io/en/latest/api/#imu-sensor
    
    using pip3
    
    '''
    import Math
    from sense_hat import SenseHat
    sense = SenseHat()
    import time
    
    from picamera.array import PiRGBArray
    from picamera import PiCamera
    
    from MagneticField import pyIGRF
    import json
    
    import cv2

    
    
    def SaveGeomagnetic(PreCalc):
        with open('data.json', 'w') as datafile:
            json_string = json.dumps(PreCalc, indent=4, sort_keys=True)
            datafile.write(json_string)
            datafile.close()
    
    def loadGeomagnetic():
        with open('data.json', 'r') as datafile:
            return json.loads(datafile.read())
    
    
    '''
    
    ignore this as it  was some preprossesing for the magnetic fields
    
    PreCalc = []
    Done = []
    
    
    compasRaw = raw = sense.get_compass_raw()
    mag = pyIGRF.MagneticField
    decs, hozs, X,Y,Z, inc, dec, hoz, eff = mag.GetGrid(-90,0,90,1, 7000, 2024)
    
    #for i in range(0, len(X)):
        #print("dec: " + str(decs[i]) + " hoz: " + str(hozs[i]) + " X: " + str(X[i]) + " inc: " + str(inc[i]) + " dec: " + str(dec[i]) + " hoz: " + str(hoz[i]) + " eff: " + str(eff[i]))
        #PreCalc.append({"deg": decs[i], "v": Math.Vector(X[i],Y[i],Z[i]).unitVector().toDict()})
    
    #SaveGeomagnetic(PreCalc)
    '''
    
    #lets load the geomagnetic data
    geomagneticData = loadGeomagnetic()
    
    camera = PiCamera()
    camera.resolution = (2592, 1944)
    
    
    compasRaw = sense.get_compass_raw()

    
    # the main loop: This is looping for ten minutes (hopefully)
    
    eldata = []
    start = time.time()

    while (time.time() - start < 30):
    
        closestObject = {}
        closestAngle = 1000000000
        
        # for some reason i didn't get the direct read working so we are doing it this wy :)
        camera.capture(str(len(eldata))+'.jpg')
        image = cv2.imread("image.jpg")
        
    
        for data in geomagneticData:
            s = data['v']
    
            v = Math.Vector(float(s['x']), float(s['y']), float(s['z']))
    
            angl = (v.Angle(Math.Vector(compasRaw['x'], compasRaw['y'], -compasRaw['z']))*180)/3.14
    
            if(angl < closestAngle):
                closestAngle = angl
                closestObject = data
    
        # Shall we do the feature matching? I think so!
     
        # Saving data so we can prosess it afterwards
        eldata.append({"img": str(len(eldata)) + '.jpg', "angl": closestAngle})    

        print(time.time() - start)
        #print(str(closest) + " and the angle: " + str(geomagneticData[closestidx]))

    # shall we analyzee the images? I think so...

    images = []

    # firstly lets load all the images into memory as it is the best thing to do. 
    # (The board ain't my, so i dont care if it dies).
    # Lets hope we have enough ram xd

    for i in range(0, len(eldata)):
        print(eldata[i]["img"])
        images.append(cv2.imread(str(eldata[i]["img"])))


    # So, we should do el image analyzing.
    #this is direcly from the docs, so dont reason me :))

    # currenty lis is for only two photos, but we will need more as in ten minutes the space station will move a lot
    # but currently I want it to work only with two photos

    orb = cv2.ORB_create()
    
    kp1, des1 = orb.detectAndCompute (images[0], None)
    kp2, des2 = orb.detectAndCompute (images[1], None)


    # create BFMatcher object
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    # Match descriptors.
    matches = bf.match(des1,des2)
    # Sort them in the order of their distance.
    matches = sorted(matches, key = lambda x:x.distance)

    sumX = 0
    # Print position changes and find the average...
    for i, change in enumerate(matches):
        #print(f"Position change for match {i+1}: {change}")
        sumX += change.distance
    
    avg = sumX/len(position_changes)

    print("avg: ")
    print(avg)

    filtered = []

    for i, change in enumerate(matches):
        if(change.distance < avg/1.4):
            filtered.append(change)

    position_changes = []
    
    for match in filtered:
        # Get the keypoints for this match
        kp1_idx = match.queryIdx
        kp2_idx = match.trainIdx
        kp1_pos = kp1[kp1_idx].pt
        kp2_pos = kp2[kp2_idx].pt
        
        # Compute position change
        pos_change = (kp2_pos[0] - kp1_pos[0], kp2_pos[1] - kp1_pos[1])
        
        # Append position change to the list
        position_changes.append(pos_change)

    
    
    # Draw first 10 matches.
    img3 = cv2.drawMatches(images[0],kp1,images[1],kp2,filtered[:143],None,flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
    img3 = cv2.resize(img3, (1920, 1080))
    cv2.imshow("name", img3)
    cv2.waitKey(0)

