#!/usr/bin/env python

import grass.script as gscript


def main():
    gscript.run_command('g.region', flags='p')
    gscript.run_command('r.mapcalc', expression='hazard = slope_DEM_reclassified@PERMANENT *0.25 + fire_probability_reclassified@PERMANENT *0.5+ CLC_2018_tarragona_reclassified@PERMANENT *25', overwrite=True)
    gscript.run_command('r.mapcalc', expression='risk = hazard@PERMANENT * building_density_reclassified@PERMANENT * firestations_distance_reclassified@PERMANENT ', overwrite=True)
if __name__ == '__main__':
    main()
