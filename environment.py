import pygame
from pygame.locals import QUIT
from shapely.geometry import LineString, Polygon, Point

class Environment:
    def __init__(self, width, height) -> None:
        self.width = width
        self.height = height
        self.walls = []
        self.padding = 50
        self.safeZoneSize = 50
        self.create_floorplan()
    
    def get_dimensions(self):
        return (self.width,self.height)
    def create_floorplan(self):
        # Create LineString objects for the walls
        left_wall = LineString([(0+self.padding, 0+self.padding), (0+self.padding, self.height-self.padding)])
        bottom_wall = LineString([(0+self.padding, self.height-self.padding), (self.width-self.padding, self.height-self.padding)])
        right_wall = LineString([(self.width - self.padding, self.height-self.padding), (self.width-self.padding, 0+self.padding)])
        top_wall = LineString([(self.width-self.padding, 0+self.padding), (0+self.padding, 0+self.padding)])
        
        # create a safe zone in the middle
        safe_zone_left_wall = LineString([(self.width/2 - self.safeZoneSize/2, self.height/2 - self.safeZoneSize/2), (self.width/2 - self.safeZoneSize/2, self.height/2 + self.safeZoneSize/2)])
        safe_zone_bottom_wall = LineString([(self.width/2 - self.safeZoneSize/2, self.height/2 + self.safeZoneSize/2), (self.width/2 + self.safeZoneSize/2, self.height/2 + self.safeZoneSize/2)])
        safe_zone_right_wall = LineString([(self.width/2 + self.safeZoneSize/2, self.height/2 + self.safeZoneSize/2), (self.width/2 + self.safeZoneSize/2, self.height/2 - self.safeZoneSize/2)])
        safe_zone_top_wall = LineString([(self.width/2 + self.safeZoneSize/2, self.height/2 - self.safeZoneSize/2), (self.width/2 - self.safeZoneSize/2, self.height/2 - self.safeZoneSize/2)])

        self.walls = [left_wall,bottom_wall,right_wall,top_wall, safe_zone_left_wall, safe_zone_bottom_wall, safe_zone_right_wall, safe_zone_top_wall]
    def get_environment(self):
        return self.walls
    
    def checkCollision(self, pos):
        for line in self.walls:
            if line.distance(Point(pos.x, pos.y)) <= 5:
                return True
    
    def draw(self,screen):
        # Draw the walls
        for wall in self.walls:
            pygame.draw.line(screen,(255,0,0),(int(wall.xy[0][0]),int(wall.xy[1][0])),(int(wall.xy[0][1]),int(wall.xy[1][1])),4)# (screen, (255, 0, 0), False, wall.xy, 4)



