#!/usr/bin/env python
# coding: utf-8

# In[3]:


# import modules
import pandas as pd
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, Point

number_of_points = 100000
blackhole_point = Point(598634.467,6192216.858)
kommune = "Samsø"


# In[10]:


# load geometry with municipalities
print("Loader kortdata..")
kom = gpd.read_file("kom/KOMMUNE.shp", usecols=["KOMNAVN"]) # this is too detailed geometry
kom = kom.dissolve(by="KOMNAVN")
kom = kom.reset_index()
# vi vil kun have samsø
samso = kom[kom["KOMNAVN"] == kommune]


# In[16]:


print(f'Genererer {number_of_points} punkter..')
# create a geodataframe with the same bounds as sgeo
bounds = samso.geometry.bounds.iloc[0]
bounding_polygon = Polygon([(bounds.minx, bounds.miny), 
                            (bounds.minx, bounds.maxy), 
                            (bounds.maxx, bounds.maxy), 
                            (bounds.maxx, bounds.miny)])
num_points = number_of_points  # Adjust as needed

# put random points in the bounding polygon
random_points = []
while len(random_points) < num_points:
    # Generate a random point with uniform x and y coordinates
    point = Point([np.random.uniform(bounds.minx, bounds.maxx),
                   np.random.uniform(bounds.miny, bounds.maxy)])
    # Check if the point is inside the polygon
    # if bounding_polygon.contains(point):
    random_points.append(point)

# create a geodataframe with the random points
noisy_polygon_gdf = gpd.GeoDataFrame(random_points, columns=['geometry'])


# In[17]:


print("Fjerner punkter udenfor øen..")
intersection = samso.geometry.iloc[0].intersection(noisy_polygon_gdf.geometry)
samsonoise = intersection[~intersection.is_empty]


# In[7]:


def pull_towards_center(points, center, G=1):
    """
    Move points towards a central point based on a gravitational-like pull.
    
    Parameters:
    - points: list of Shapely Point objects to be moved.
    - center: Shapely Point object representing the central point.
    - G: gravitational constant to adjust the strength of the pull.
    
    Returns:
    - List of new Shapely Point objects after being moved.
    """
    new_points = []
    for point in points:
        # Calculate distance and direction to the center
        dx = center.x - point.x
        dy = center.y - point.y
        distance = point.distance(center)
        
        # Calculate the force using the gravitational formula
        # Assuming m1 = m2 = 1 for simplicity
        F = G / (distance**2)
        
        # Move the point towards the center based on the force
        new_x = point.x + F * dx
        new_y = point.y + F * dy
        
        dx2 = center.x - new_x
        dy2 = center.y - new_y
        # is the new point on the other side of the center now?
        if dx * dx2 < 0 or dy * dy2 < 0:
            #new_x = center.x
            #new_y = center.y
            continue

        new_points.append(Point(new_x, new_y))
    
    return new_points


# In[18]:


def plot_it(datapoints, index=0):
    fig,ax = plt.subplots(figsize=(15,15))
    samso.plot(ax=ax, color='#eee', edgecolor='#333', linewidth=0.1)
    plotpoints = gpd.GeoDataFrame(datapoints, columns=['geometry'])
    plotpoints.plot(ax=ax,markersize=0.1,alpha=0.7,color='#880808')
    jeppe = blackhole_point
    jeppe = gpd.GeoDataFrame([jeppe], columns=['geometry'])
    jeppe.plot(ax=ax,markersize=3,color='black',marker='*')
    ax.set_axis_off()
    fig.savefig("out/plot_{:03d}.png".format(index), dpi=100, bbox_inches="tight")
    plt.close()


# In[ ]:


print("genererer animation..")
blackhole = blackhole_point
index=1
pointdata=samsonoise.copy()
for i in range(10):
    plot_it(pointdata,index)
    index+=1
while len(pointdata)>0:
    pointdata = pull_towards_center(pointdata, blackhole, G=0.5 * 1000000)
    plot_it(pointdata,index)
    index+=1

for i in range(10):
    plot_it(pointdata,index)
    index+=1

print(f'Færdig, {index} billeder gemt i out/plot_*.png')
print('Kør make_video.ps1 for at lave video (kræver ffmpeg)')

