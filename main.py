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
    
    # all the astroPi specific libraries
    from sense_hat import SenseHat
    from picamera.array import PiRGBArray
    from picamera import PiCamera

    # All custom libraries / files
    from MagneticField import pyIGRF    # I am going to delete this
    import geo                          # This is right now only for calculating distanse from cordinates
    import Math                         # Right now this includes Vector (3d) class. Yes I like to build everyithing by myself

    # python libraries this program needs for running
    import json # Have to read json file
    import time # have to measure time for the the 10 min limit
    import cv2  # image analyzing (feature detecting & matching)

    sense = SenseHat()
    
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

    while (time.time() - start < 50):
    
        closestObject = {}
        closestAngle = 1000000000
        
        # for some reason i didn't get the direct read working so we are doing it this wy :)
        camera.capture(str(len(eldata))+'.jpg')
        for data in geomagneticData:
            s = data['v']
    
            v = Math.Vector(float(s['x']), float(s['y']), float(s['z']))
    
            angl = (v.Angle(Math.Vector(compasRaw['x'], compasRaw['y'], -compasRaw['z']))*180)/3.14
    
            if(angl < closestAngle):
                closestAngle = angl
                closestObject = data
    
        # Shall we do the feature matching? I think so!
     
        # Saving data so we can prosess it afterwards
        eldata.append({"img": str(len(eldata)) + '.jpg', "angl": data['deg']})    

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
    # but currently I want it to work only with two photos, now i make it work with many photos as there is, so we get the most accurate information

    TheFUllDistance = Math.Vector(0,0,0)

    for i in range(1, len(images)):
        print("el i: " + str(i))
        
        orb = cv2.ORB_create()
        
        kp1, des1 = orb.detectAndCompute (images[i-1], None)
        kp2, des2 = orb.detectAndCompute (images[i], None)


        # create BFMatcher object
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        # Match descriptors.
        matches = bf.match(des1,des2)
        # Sort them in the order of their distance.
        matches = sorted(matches, key = lambda x:x.distance)

        sumD = 0
        # Print position changes and find the average...
        for i, change in enumerate(matches):
            #print(f"Position change for match {i+1}: {change}")
            sumD += abs(change.distance)
        
        avg = sumD/len(matches)

        print("avg: ")
        print(avg)

        filtered = []

        for i, change in enumerate(matches):
            if(abs(change.distance) < avg):
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

        # Now we get the average of the filtered data and save it.

        sumDist = Math.Vector(0,0,0)
        for i, change in enumerate(position_changes):
            #print(f"Position change for match {i+1}: {change}")
            sumDist += Math.Vector(abs(change[0]), abs(change[1]), 0)
        
        # and then make it average as we should 
        sumDist = sumDist/len(position_changes)

        TheFUllDistance += sumDist

        print("Full distance: ")
        print(TheFUllDistance)

    print("full distance")
    print(TheFUllDistance)
    # Draw first 10 matches.
    img3 = cv2.drawMatches(images[0],kp1,images[1],kp2,filtered[:143],None,flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
    img3 = cv2.resize(img3, (960, 540))
    cv2.imshow("name", img3)
    cv2.waitKey(0)

