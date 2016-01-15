import numpy as np
gnd_launcher_latlon = [29.9429917, -82.0332305] # Gnd Launcher
tower_launcher_latlon = [29.94264819, -82.03179454] # Tower Launcher
earth_radius = 6371 ##km

## finds the distance between two latlon points
def distance_between_points(latlon1, latlon2):
    ##calculation of distance using haversine formula (in km)
    """distance between two latlon points in KM"""

    latlon1=np.radians(latlon1)
    latlon2=np.radians(latlon2)

    dlat=latlon1[0]-latlon2[0]
    dlon=latlon1[1]-latlon2[1]

    a=np.sin(dlat/2) * np.sin(dlat/2) + np.sin(dlon/2) * np.sin(dlon/2) * np.cos(latlon1[0]) * np.cos(latlon2[0])
    b=2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    return b*earth_radius

## calculates the bearing between two latlon points.
def bearing(latlon1, latlon2):
    """bearing between two lat lon points"""
    dLon=latlon1[1]-latlon2[1]
    y=np.sin(dLon)*np.cos(latlon2[0])
    x=np.cos(latlon1[0])*np.sin(latlon2[0]) - np.sin(latlon1[0])*np.cos(latlon2[0])*np.cos(dLon)
    return np.atan2(y,x)
        
def DXDY(latlon1, latlon2):
    """find delta x and delta y between two lat lon points """
    
    X=np.pi*earth_radius*(latlon2[0]-latlon1[0])*np.cos(latlon1[1])/180.0
    Y=np.pi*earth_radius*(latlon2[1]-latlon1[1])/180.0
    
    return X,Y
