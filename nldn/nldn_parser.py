#!/usr/bin/env python

def parse_nldn(fileIn, fileOut):
    dates = []
    times = []
    lats = []
    lons = []
    kas = []
    types = []
    mults = []

    with open(fileIn, 'r') as f:
        """
        File Format:

        Date        Time            Mult    Long    Lat     kA  Type
        mm/dd/yyy   hh:mm:ss.ssss   00      -LL.LLL LL.LLL  0.0  CG/IC

        Desired Format:
        Date        Time            Lat     Lon     kA      Type    Mult    Unknown
        mm/dd/yy    hh:mm:ss.sss    LL.LLL  -LL.LLL 0.0     G/C     0.0     0.0
        """

        data_tmp = f.read().split('\n')
        data = data_tmp[1:]

        for d in data:
            parts = d.split()

            if parts:
                if len(parts) == 7:
                    # CG
                    dates.append('%s%s' % (parts[0][:6], parts[0][8:]))
                    times.append(parts[1])
                    lats.append(parts[4])
                    lons.append(parts[3])
                    kas.append(parts[5])
                    mults.append(float(parts[2]))
                    types.append('G')

                else:
                    # IC
                    dates.append('%s%s' % (parts[0][:6], parts[0][8:]))
                    times.append(parts[1])
                    lats.append(parts[4])
                    lons.append(parts[3])
                    kas.append(0.0)
                    mults.append(float(parts[2]))
                    types.append('C')

    with open(fileOut, 'w') as f:
        for i in range(len(dates)):
            s = '%s %s %s %s %s %s %s 0.0\n' % (dates[i], times[i], lats[i],
                                                lons[i], kas[i], types[i],
                                                mults[i])
            f.write(s)
