from scipy.odr.odrpack import ODR
import world
import sensors
import featureUtils
import pygame
import random

FeatureMap = featureUtils.findFeatures()
environment = world.buildEnvironment((800, 1000))
originalMap = environment.map.copy()
laser = sensors.LaserSensor(200, originalMap, unc=(0.5, 0.01))
environment.map.fill((0, 0, 0))
environment.infomap = environment.map.copy()
originalMap = environment.map.copy()


def rand_color():
    rang = range(32, 256, 32)
    return tuple(random.choice(rang) for _ in range(3))


running = True
FEATURE_DETECTION = True
BREAK_POINT_IND = 0

while running:
    environment.infomap = originalMap.copy()
    FEATURE_DETECTION = True
    BREAK_POINT_IND = 0
    ENDPOINTS = [0, 0]
    sensorON = False
    PREDICTED_POINTS_TODRAW = []
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    if pygame.mouse.get_focused():
        sensorON = True
    elif not pygame.mouse.get_focused():
        sensorON = False
    if sensorON:
        position = pygame.mouse.get_pos()
        laser.position = position
        sensor_data = laser.sense_obstacles()
        FeatureMap.set_points(sensor_data)
        while BREAK_POINT_IND < (FeatureMap.NP - FeatureMap.PMIN):
            seedSeg = FeatureMap.find_segement(
                laser.position, BREAK_POINT_IND)
            if seedSeg == False:
                break
            else:
                seedSegment = seedSeg[0]
                PREDICTED_POINTS_TODRAW = seedSeg[1]
                INDICES = seedSeg[2]
                results = FeatureMap.generate_segement(INDICES, BREAK_POINT_IND)
                if results == False:
                    BREAK_POINT_IND = INDICES[1]
                    continue
                else:
                    line_eq = results[1]
                    m, c = results[5]
                    line_seg = results[0]
                    OUTERMOST = results[2]
                    BREAK_POINT_IND = results[3]

                    ENDPOINTS[0] = FeatureMap.projection_point2line(OUTERMOST[0], m, c)
                    ENDPOINTS[1] = FeatureMap.projection_point2line(OUTERMOST[1], m, c)

                    FeatureMap.FEATURES.append([[m,c],ENDPOINTS])
                    pygame.draw.line(environment.infomap,(0, 255, 0), ENDPOINTS[0], ENDPOINTS[1], 1)
                    environment.dataStorage(sensor_data)

                    FeatureMap.FEATURES=FeatureMap.lineFeature2point()
                    featureUtils.landmark_association(FeatureMap.FEATURES)


        environment.show_sensorData()
        for landmark in featureUtils.Landmarks:
            pygame.draw.line(environment.infomap,(0, 255, 0), landmark[1][0], landmark[1][1], 2)
            
                        
                    #COLOR = rand_color()
                    #for point in line_seg:
                        #environment.infomap.set_at((int(point[0][0]), int(point[0][1])), (0, 255, 0))
                        #pygame.draw.circle(environment.infomap, COLOR, (int(point[0][0]), int(point[0][1])), 2, 0)

    environment.map.blit(environment.infomap, (0, 0))
    pygame.display.update()

pygame.quit()
