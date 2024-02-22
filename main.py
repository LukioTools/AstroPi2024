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
    from MagneticField import pyIGRF    # I am going to delete this, This is by the way based on the International Geomagnetic Reference Field (IGRF). Dont ask me how it works :)))  
    import geo                          # This is right now only for calculating distanse from cordinates
    import Math                         # Right now this includes Vector (3d) class. Yes I like to build everyithing by myself

    # python libraries this program needs for running
    import json # Have to read json file
    import time # have to measure time for the the 10 min limit
    import cv2  # image analyzing (feature detecting & matching)
    import os
    sense = SenseHat()
    
    # saving json (not in use)
    def SaveGeomagnetic(PreCalc):
        with open('data.json', 'w') as datafile:
            json_string = json.dumps(PreCalc, indent=4, sort_keys=True)
            datafile.write(json_string)
            datafile.close()
    
    # loading json
    def loadGeomagnetic():
        with open('data.json', 'r') as datafile:
            return json.loads(datafile.read())
    
    def FindBestLatidude():
        closestObject = {}
        closestAngle = 1000000000

        compasRaw = sense.get_compass_raw()
        
        # for some reason i didn't get the direct read to cv2 object working so we are doing it this wy :)
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
        return {"img": str(len(eldata)) + '.jpg', "lat": data['deg']}
    
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

    # This is for measuring the speed
    TheStartTimer = time.time() * 1000
    
    #lets load the geomagnetic data
    geomagneticData = loadGeomagnetic()
    
    #initialize the picamera and set resolution
    camera = PiCamera()
    camera.resolution = (2592, 1944)
    
    # this is the image name and the latidue of the position
    eldata = []

    # for measuring time
    startTime = time.time()
    UsedTime = 0

    # the main loop: This is looping for ten minutes (hopefully)
    while (time.time() - startTime < 50):
        eldata.append(FindBestLatidude()) # this basicly does everything. Made it funktion so its easier to read. Even trough its kinda stupid
        print(time.time() - start)

    # Get how many seconds we spent there
    UsedTime = TheStartTimer - time.time() * 1000

    # shall we analyze the images? I think so...

    images = []

    # firstly lets load all the images into memory as it is the best thing to do. 
    # (The board ain't my, so i dont care if it dies).
    # Lets hope we have enough ram xd

    for i in range(0, len(eldata)):
        images.append(cv2.imread(str(eldata[i]["img"])))


    # So, we should do el image analyzing.

    TheFUllDistance = Math.Vector(0,0,0)

    for i in range(1, len(images)):
        
        orb = cv2.ORB_create()
        
        kp1, des1 = orb.detectAndCompute (images[i-1], None)
        kp2, des2 = orb.detectAndCompute (images[i], None)


        # create BFMatcher object
        # atleast when it came to me, it wasn't abble to find bf for me. 
        # Reason might be that i'm boy and I like girls, or it might be bug in the system
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

    # The cordinates...
    RealDistanceY = geo.distance(eldata[0]['lat'], 0, eldata[-1]['lat'], 0)
    RealDistanceX = (RealDistanceY*TheFUllDistance.x)/TheFUllDistance.y

    RealDistance = Math.Vector(RealDistanceX, RealDistanceY)

    # get the traveled distance
    MagnitudeOfDistance = RealDistance.magnitude()

    # the unit is m/s
    TheVelocity = MagnitudeOfDistance/UsedTime

    #lets save the data
    with open("result.txt", "w") as file:
        # Write numbers from 1 to 10, each on a new line
        file.write(str(TheVelocity))

    # and finaly lets delete all images, so we are on the safe side...
    for i in images:
        print(xd)
        os.remove(images["img"])

    


