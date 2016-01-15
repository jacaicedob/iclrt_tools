import numpy as np
# import geopy as gp

class Location(object):
    def __init__(self, lat, lon, alt=0.0):
        """
        :param lat: Latitude in degrees
        :param lon: Longitude in degrees
        :param alt: Altitude in meters
        :return: nothing
        """
        self.lat = float(lat)
        self.latr = np.radians(self.lat)

        self.lon = float(lon)
        self.lonr = np.radians(self.lon)

        self.alt = float(alt)

    def distance_to_location_2d(self, lat, lon):
        """
        Calculates and returns the 2D distance between the location of interest
        and self using the Haversine formula

        :param lat: Latitude of location of interest in degrees
        :param lon: Longitude of location of interest in degrees
        :return: Distance between the two locations in meters
        """

        # return gp.distance.distance((self.lat, self.lon), (lat, lon)).meters

        EARTH_RADIUS = 6371.0E3  # meters

        latr = np.radians(90 - lat)
        lonr = np.radians(lon)

        gamma = np.arccos(np.cos(np.pi/2.0 - self.latr) * np.cos(latr) + \
                        np.sin(np.pi/2.0 - self.latr) * np.sin(latr) * \
                        np.cos(self.lonr - lonr))

        return gamma * EARTH_RADIUS

        # latr = np.radians(lat)
        # lonr = np.radians(lon)
        #
        # d_lat = self.latr - latr
        # d_lon = self.lonr - lonr
        #
        # a = np.sin(d_lat/2) * np.sin(d_lat/2) + \
        #     np.sin(d_lon/2) * np.sin(d_lon/2) * np.cos(self.latr) * \
        #     np.cos(latr)
        #
        # b = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
        #
        # return b * EARTH_RADIUS

    def bearing(self, lat, lon):
        """
        :param lat: Latitude of location of interest in degrees
        :param lon: Longitude of location of interest in degrees
        :return: Bearing from self to lat, lon
        """
        latr = np.radians(lat)
        lonr = np.radians(lon)

        d_lon = lonr - self.lonr
        y = np.sin(d_lon) * np.cos(latr)
        x = np.cos(self.lonr) * np.sin(lonr) - \
            np.sin(self.lonr) * np.cos(lonr) * np.cos(d_lon)

        return np.arctan2(y, x)

    def xyz_transform(self):
        """
        :return: tuple with x,y,z coordinates
        """

        # WGS84 datum
        a = 6378137.0  # semi-major axis of ellipsoid in meters
        b = 6356752.314245  # semi-minor axis of ellipsoid in meters
        f = 1.0/298.257223563  # flattening of ellipsoid

        # e2 = 2*f - f**2
        e2 = (a**2 - b**2) / a**2
        # print(e2)
        nu = a / np.sqrt(1.0 - e2*np.sin(self.latr)*np.sin(self.latr))

        x = (nu + self.alt) * np.cos(self.latr) * np.cos(self.lonr)
        y = (nu + self.alt) * np.cos(self.latr) * np.sin(self.lonr)
        z = (nu * (1 - e2) + self.alt) * np.sin(self.latr)

        return x, y, z

gnd_launcher_latlon = [29.9429917, -82.0332305, 0]  # Gnd Launcher
tower_launcher_latlon = [29.94264819, -82.03179454, 0]  # Tower Launcher

if __name__ == "__main__":
    # a = Location(38.898556, -77.037852)
    # b = Location(38.897147, -77.043934)

    a = Location(gnd_launcher_latlon[0], gnd_launcher_latlon[1],
                 gnd_launcher_latlon[2])
    b = Location(tower_launcher_latlon[0], tower_launcher_latlon[1],
                 tower_launcher_latlon[2])
    c = Location(29.9565023, -82.0334902, 0)

    # gc_dist = a.distance_to_location_2d(b.lat, b.lon)

    # x, y, z = a.xyz_transform()
    # x1, y1, z1 = b.xyz_transform()

    # cart_gnd_dist = np.sqrt((x - x1)**2 + (y - y1)**2)
    # cart_dist = np.sqrt((x - x1)**2 + (y - y1)**2 + (z - z1)**2)

    print('Bearing: {0:0.2f} radians'.format(a.bearing(b.lat, b.lon)*180/np.pi))
    print('Bearing: {0:0.2f} radians'.format(a.bearing(c.lat, c.lon)*180/np.pi))

    # print('\nGround (x, y, z) = ({0:0.02f}, {1:0.02f}, {2:0.02f}) m'.format(x, y, z))
    # print('Tower  (x, y, z) = ({0:0.02f}, {1:0.02f}, {2:0.02f}) m'.format(x1, y1, z1))
    #
    # print('\nGreat circle distance: {0:0.2f} m'.format(gc_dist))
    # print('GWS84 Cartesian total distance: {0:0.2f}'.format(cart_dist))
    # print('Difference: {0:0.02f} m'.format(gc_dist - cart_dist))
    #
    # print('\nGWS84 Cartesian x,y distance: {0:0.2f} m'.format(cart_gnd_dist))

# ## finds the distance between two latlon points
# def distance_between_points(latlon1, latlon2):
#     ##calculation of distance using haversine formula (in km)
#     """distance between two latlon points in KM"""
#
#     latlon1 = np.radians(latlon1)
#     latlon2 = np.radians(latlon2)
#
#     dlat = latlon1[0]-latlon2[0]
#     dlon = latlon1[1]-latlon2[1]
#
#     a = np.sin(dlat/2) * np.sin(dlat/2) + np.sin(dlon/2) * np.sin(dlon/2) * np.cos(latlon1[0]) * np.cos(latlon2[0])
#     b = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
#     return b*earth_radius
#
# ## calculates the bearing between two latlon points.
# def bearing(latlon1, latlon2):
#     """bearing between two lat lon points"""
#     dLon = latlon1[1]-latlon2[1]
#     y = np.sin(dLon)*np.cos(latlon2[0])
#     x = np.cos(latlon1[0])*np.sin(latlon2[0]) - np.sin(latlon1[0])*np.cos(latlon2[0])*np.cos(dLon)
#     return np.atan2(y,x)
#
# def DXDY(latlon1, latlon2):
#     """find delta x and delta y between two lat lon points """
#
#     X = np.pi*earth_radius*(latlon2[0]-latlon1[0])*np.cos(latlon1[1])/180.0
#     Y = np.pi*earth_radius*(latlon2[1]-latlon1[1])/180.0
#
#     return X, Y
